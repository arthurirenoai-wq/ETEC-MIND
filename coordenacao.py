import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import webbrowser
import urllib.parse

# Configuração do Banco de Dados
DB_URL = "postgresql://neondb_owner:npg_rtgT9R3GEhAV@ep-snowy-dream-a5reiccc-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

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
    # Limpa a tabela antes de atualizar
    for item in tabela.get_children():
        tabela.delete(item)
    
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, materia, nivel, status FROM relatos ORDER BY data_envio DESC")
        
        for linha in cursor.fetchall():
            id_relato, nome, email, materia, nivel, status = linha
            nome_exibicao = f"Anônimo {id_relato}" if nome == "Anônimo" else nome
            tabela.insert("", "end", values=(id_relato, nome_exibicao, email, materia, nivel, status))
            
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível buscar os dados no Neon:\n{e}")

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
janela.geometry("850x450")
janela.configure(padx=15, pady=15)

# Prepara o banco de dados ANTES de carregar a interface
criar_tabela_se_nao_existir()

tk.Label(janela, text="Sistema de Recebimento de Relatos", font=("Arial", 16, "bold")).pack(pady=5)

# Tabela
colunas = ("ID", "Aluno", "E-mail", "Matéria", "Dificuldade", "Status")
tabela = ttk.Treeview(janela, columns=colunas, show="headings", height=12)

# Configura o tamanho de cada coluna
for col in colunas:
    tabela.heading(col, text=col)
    tabela.column(col, width=130, anchor="center")

tabela.pack(fill=tk.BOTH, expand=True, pady=10)

# Botões
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=10)

tk.Button(frame_botoes, text="🔄 Atualizar Lista", command=carregar_dados, width=15).pack(side=tk.LEFT, padx=10)
tk.Button(frame_botoes, text="✉️ Enviar E-mail", command=enviar_email, width=15, bg="#28a745", fg="white").pack(side=tk.LEFT, padx=10)
tk.Button(frame_botoes, text="✔ Marcar Resolvido", command=marcar_resolvido, width=18, bg="#0056b3", fg="white").pack(side=tk.LEFT, padx=10)

# Carrega os dados na tabela
carregar_dados()

# Mantém a janela aberta
janela.mainloop()
