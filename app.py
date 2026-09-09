from flask import Flask, request, jsonify, render_template
import psycopg2

# Configura o Flask para ler os HTMLs na mesma pasta
app = Flask(__name__, template_folder='.')

# Sua chave de acesso ao Neon
DB_URL = "postgresql://neondb_owner:npg_rtgT9R3GEhAV@ep-snowy-dream-a5reiccc-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def conectar_banco():
    return psycopg2.connect(DB_URL)

# Rota para a tela do aluno
@app.route('/')
def aluno():
    return render_template('formulario_3.html')

# Rota para a tela da secretaria
@app.route('/coordenacao')
def painel():
    return render_template('coordenacao.html')

# Rota invisível (API) que salva os dados no Neon
@app.route('/api/salvar', methods=['POST'])
def salvar_relato():
    dados = request.json
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO relatos (nome, email, materia, nivel, detalhes) VALUES (%s, %s, %s, %s, %s)",
        (dados['nome'], dados['email'], dados['materia'], dados['nivel'], dados['detalhes'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Salvo com sucesso no Neon!"})

# Rota invisível (API) que busca os dados para a secretaria
@app.route('/api/listar', methods=['GET'])
def listar_relatos():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, materia, nivel, detalhes, TO_CHAR(data_envio, 'DD/MM/YYYY HH24:MI') FROM relatos WHERE status = 'Pendente' ORDER BY data_envio DESC")
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Formata a lista para enviar ao HTML
    relatos = [{"id": l[0], "nome": l[1], "email": l[2], "materia": l[3], "nivel": l[4], "detalhes": l[5], "data": l[6]} for l in linhas]
    return jsonify(relatos)

if __name__ == '__main__':
    app.run(debug=True)
