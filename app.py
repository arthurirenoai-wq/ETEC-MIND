from flask import Flask, request, jsonify, render_template, redirect
import psycopg2

app = Flask(__name__, template_folder='.')

# Sua chave de acesso ao Neon
DB_URL = "postgresql://neondb_owner:npg_rtgT9R3GEhAV@ep-snowy-dream-a5reiccc-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def conectar_banco():
    return psycopg2.connect(DB_URL)

# ==========================================
# FUNÇÃO PARA CRIAR A TABELA AUTOMATICAMENTE
# ==========================================
def criar_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()
    # O comando "IF NOT EXISTS" garante que ele só crie a tabela se ela ainda não existir
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
    print("Banco de dados verificado/atualizado com sucesso!")

# Rota 1: Entrega a tela do formulário do aluno
@app.route('/')
def aluno():
    return render_template('formulario.html')

# Rota 2: Recebe os dados do aluno e salva no Neon
@app.route('/api/salvar', methods=['POST'])
def salvar_relato():
    dados = request.json
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO relatos (nome, email, materia, nivel, detalhes, status) VALUES (%s, %s, %s, %s, %s, 'Pendente')",
        (dados['nome'], dados['email'], dados['materia'], dados['nivel'], dados['detalhes'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Salvo com sucesso!"})

# Rota 3: Tela da Coordenação (O Python busca os dados e monta o HTML)
@app.route('/coordenacao')
def painel():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, materia, nivel, detalhes, TO_CHAR(data_envio, 'DD/MM/YYYY HH24:MI') FROM relatos WHERE status = 'Pendente' ORDER BY data_envio DESC")
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Formata a lista para o HTML
    relatos = [{"id": l[0], "nome": l[1], "email": l[2], "materia": l[3], "nivel": l[4], "detalhes": l[5], "data": l[6]} for l in linhas]
    
    return render_template('coordenacao.html', relatos=relatos)

# Rota 4: Marca como resolvido e recarrega a página
@app.route('/resolver/<int:id_relato>')
def resolver_relato(id_relato):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("UPDATE relatos SET status = 'Resolvido' WHERE id = %s", (id_relato,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/coordenacao')

if __name__ == '__main__':
    # Roda a verificação do banco de dados antes de ligar o servidor
    criar_tabela()
    app.run(debug=True)
