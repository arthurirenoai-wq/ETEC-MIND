import streamlit as st
import psycopg2
import urllib.parse
import sys
from streamlit.web import cli as stcli

st.set_page_config(page_title="Painel ETEC MIND", page_icon="🏫", layout="centered")

with st.sidebar:
    st.title("📌 ETEC MIND")
    st.markdown("### Fextec ...")
    st.info("Bem-vindo ao painel exclusivo da coordenação para acompanhamento das dificuldades dos alunos.")
    st.divider()
    st.markdown("🔒 *Ambiente restrito*")

DB_URL = "postgresql://neondb_owner:npg_rtgT9R3GEhAV@ep-snowy-dream-a5reiccc-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def conectar_banco():
    return psycopg2.connect(DB_URL)

def criar_tabela_se_nao_existir():
    conn = conectar_banco()
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

def carregar_todos_relatos():
    conn = conectar_banco()
    cursor = conn.cursor()
    # Agora busca todos os relatos para você ver o histórico do que foi resolvido
    cursor.execute("SELECT id, nome, email, materia, nivel, detalhes, status, TO_CHAR(data_envio, 'DD/MM/YYYY HH24:MI') FROM relatos ORDER BY data_envio DESC")
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    return linhas

def atualizar_status(id_relato, novo_status):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("UPDATE relatos SET status = %s WHERE id = %s", (novo_status, id_relato))
    conn.commit()
    cursor.close()
    conn.close()
    st.rerun()

criar_tabela_se_nao_existir()

st.title("🏫 Painel de Recebimento")
st.markdown("**Sistema ETEC MIND** | Clique em um relato para ver os detalhes.")
st.divider()

relatos = carregar_todos_relatos()

if not relatos:
    st.success("🎉 Nenhum relato foi recebido ainda.")
else:
    for relato in relatos:
        id_relato, nome, email, materia, nivel, detalhes, status, data = relato
        
        nome_exibicao = f"Anônimo {id_relato}" if nome == "Anônimo" else nome
        
        # Identificação visual de status
        if status == 'Resolvido':
            icone_status = "✅ Resolvido"
        elif status == 'Em andamento':
            icone_status = "⏳ Em andamento"
        else:
            icone_status = "🚨 Pendente"

        # A mágica do "mostrar brevemente": O Expander!
        with st.expander(f"{icone_status} | 📚 {materia} - {nome_exibicao}"):
            
            texto_email = f"({email})" if email and email != "Não informado" else "(Sem e-mail)"
            st.write(f"**Aluno:** {nome_exibicao} {texto_email}")
            st.write(f"**Data:** {data} | **Dificuldade:** {nivel}")
            st.warning(detalhes)
            
            # Trava a edição se já estiver resolvido
            if status == 'Resolvido':
                st.success("Este problema já foi solucionado e arquivado.")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    if status == 'Pendente':
                        if st.button("🛠️ Iremos resolver seu problema", key=f"btn_andamento_{id_relato}"):
                            atualizar_status(id_relato, 'Em andamento')
                    
                    if email and email != "Não informado":
                        assunto = urllib.parse.quote(f"ETEC MIND - Atualização do seu relato de {materia}")
                        mensagem = urllib.parse.quote(f"Olá, {nome_exibicao}!\n\nA coordenação está analisando o seu relato e iremos resolver seu problema o mais rápido possível.")
                        st.markdown(f"""
                            <a href="mailto:{email}?subject={assunto}&body={mensagem}" 
                               style="background-color:#0056b3; color:white; padding:8px 15px; border-radius:5px; text-decoration:none; display:inline-block; margin-top:5px;">
                               ✉️ Avisar Aluno por E-mail
                            </a>
                            """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("✔ Marcar como Resolvido", key=f"btn_resolver_{id_relato}", type="primary"):
                        atualizar_status(id_relato, 'Resolvido')

if __name__ == '__main__':
    if "streamlit" not in sys.argv[0].lower():
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
