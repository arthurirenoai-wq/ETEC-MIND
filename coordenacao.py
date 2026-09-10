import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import webbrowser
import urllib.parse

# Configuração do Banco de Dados
DB_URL = "postgresql://neondb_owner:npg_rtgT9R3GEhAV@ep-snowy-dream-a5reiccc-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Dicionário invisível para guardar os textos longos dos relatos
textos_dos_relatos = {}

def criar_tabela_se_nao_existir():
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relatos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(150) NOT NULL,
                email VARCHAR(150),
                materia VARCHAR(100) NOT NULL,
                nivel VARCHAR(50) NOT NULL,
                detalhes TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'Pendente',
                data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível criar a tabela no Neon:\n{e}")

def carregar_dados():
    # Limpa a tabela e a memória antes de atualizar
    for item in tabela.get_children():
        tabela.delete(item)
    textos_dos_relatos.clear()
    
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        # Agora buscamos a coluna 'detalhes' também
        cursor.execute("SELECT id, nome, email, materia, nivel, status, detalhes FROM relatos ORDER BY data_envio DESC")
        
        for linha in cursor.fetchall():
            id_relato, nome, email, materia, nivel, status, detalhes = linha
            nome_exibicao = f"Anônimo {id_relato}" if nome == "Anônimo" else nome
            
            # Insere na tabela visual
            tabela.insert("", "end", values=(id_relato, nome_exibicao, email, materia, nivel, status))
            
            # Guarda o texto longo na memória usando o ID como chave
            textos_dos_relatos[str(id_relato)] = detalhes
            
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível buscar os dados no Neon:\n{e}")

def ver_detalhes(event=None):
    selecionado = tabela.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um relato na tabela primeiro!")
        return
        
    valores = tabela.item(selecionado[0])['values']
    id_relato = str(valores[0])
    nome = valores[1]
    materia = valores[3]
    
    # Puxa o texto da memória
    texto_completo = textos_dos_relatos.get(id_relato, "Texto não encontrado.")
    
    # Cria uma nova janelinha para leitura
    janela_leitura = tk.Toplevel(janela)
    janela_leitura.title(f"Lendo Relato - {nome}")
    janela_leitura.geometry("450x350")
    janela_leitura.configure(padx=20, pady=20)
    
    tk.Label(janela_leitura, text=f"📚 {materia}", font=("Arial", 14, "bold")).pack(anchor="w")
    tk.Label(janela_leitura, text=f"Aluno: {nome}", font=("Arial", 11)).pack(anchor="w", pady=(0, 15))
    
    # Caixa de texto para o relato
    caixa_texto = tk.Text(janela_leitura, wrap="word", font=("Arial", 11), bg="#f9f9f9", padx=10, pady=10)
    caixa_texto.insert("1.0", texto_completo)
    caixa_texto.config(state="disabled") # Trava para não deixarem editar sem querer
    caixa_texto.pack(fill=tk.BOTH, expand=True)

def excluir_relato():
    selecionado = tabela.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um relato para excluir!")
        return
        
    id_relato = tabela.item(selecionado[0])['values'][0]
    
    # Pergunta de segurança
    resposta = messagebox.askyesno("Excluir Relato", "Tem certeza que deseja apagar este relato definitivamente?\n\nIsso não poderá ser desfeito.")
    
    if resposta:
        try:
            conn = psycopg2.connect(DB_URL)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM relatos WHERE id = %s", (id_relato,))
            conn.commit()
            conn.close()
            
            carregar_dados() # Atualiza a tabela sumindo com o registro
            messagebox.showinfo("Sucesso", "Relato excluído com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir o relato:\n{e}")

def marcar_resolvido():
    selecionado = tabela.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um relato na tabela primeiro!")
        return
        
    id_relato = tabela.item(selecionado[0])['values'][0]
    
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("UPDATE relatos SET status = 'Resolvido' WHERE id = %s", (id_relato,))
        conn.commit()
        conn.close()
        
        carregar_dados()
        messagebox.showinfo("Sucesso", "Relato atualizado para Resolvido!")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao atualizar o relato:\n{e}")

def enviar_email():
    selecionado = tabela.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um relato na tabela primeiro!")
        return
        
    valores = tabela.item(selecionado[0])['values']
    nome, email, materia = valores[1], valores[2], valores[3]
    
    if email and email != "Não informado":
        assunto = urllib.parse.quote(f"ETEC MIND - Retorno sobre {materia}")
        mensagem = urllib.parse.quote(f"Olá, {nome}!\n\nA coordenação está analisando o seu relato.")
        webbrowser.open(f"mailto:{email}?subject={assunto}&body={mensagem}")
    else:
        messagebox.showwarning("Aviso", "Este aluno não forneceu um e-mail válido.")

# ==========================================
# CONSTRUÇÃO DA INTERFACE (JANELA)
# ==========================================
janela = tk.Tk()
janela.title("🏫 Painel Coordenação - ETEC MIND")
janela.geometry("900x500") # Aumentei um pouco a largura para caber os botões
janela.configure(padx=15, pady=15)

criar_tabela_se_nao_existir()

tk.Label(janela, text="Sistema de Recebimento de Relatos", font=("Arial", 16, "bold")).pack(pady=5)

# Tabela
colunas = ("ID", "Aluno", "E-mail", "Matéria", "Dificuldade", "Status")
tabela = ttk.Treeview(janela, columns=colunas, show="headings", height=12)

for col in colunas:
    tabela.heading(col, text=col)
    tabela.column(col, width=130, anchor="center")

tabela.pack(fill=tk.BOTH, expand=True, pady=10)

# Atalho: Se der duplo-clique no aluno, abre a leitura do relato!
tabela.bind("<Double-1>", ver_detalhes)

# Botões
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=10)

tk.Button(frame_botoes, text="🔄 Atualizar", command=carregar_dados, width=12).pack(side=tk.LEFT, padx=5)
tk.Button(frame_botoes, text="👁️ Ler Relato", command=ver_detalhes, width=12, bg="#17a2b8", fg="white").pack(side=tk.LEFT, padx=5)
tk.Button(frame_botoes, text="✉️ E-mail", command=enviar_email, width=12, bg="#28a745", fg="white").pack(side=tk.LEFT, padx=5)
tk.Button(frame_botoes, text="✔ Resolvido", command=marcar_resolvido, width=12, bg="#0056b3", fg="white").pack(side=tk.LEFT, padx=5)
tk.Button(frame_botoes, text="🗑️ Excluir", command=excluir_relato, width=12, bg="#dc3545", fg="white").pack(side=tk.LEFT, padx=5)

carregar_dados()

janela.mainloop()
