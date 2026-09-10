import streamlit as st
import psycopg2
import urllib.parse
import sys
from streamlit.web import cli as stcli

# 1. Configuração visual da página
st.set_page_config(page_title="Painel ETEC MIND", page_icon="🏫", layout="centered")

# ==========================================
# TELINHA DE INFORMAÇÕES (Menu Lateral)
# ==========================================
with st.sidebar:
    st.title("📌 ETEC MIND")
    st.markdown("### Fextec ...")
    st.info("""
    **Bem-vindo ao ETEC MIND!**
    
    Este é o painel exclusivo da coordenação para acompanhamento das dificuldades dos alunos.
    
    - Ajude a melhorar nossos estudos.
    - Compartilhe suas dificuldades.
    - Transforme a educação!
    """)
    st.divider()
    st.markdown("🔒 *Ambiente restrito da Coordenação*")

# Sua chave de acesso ao Neon
DB_URL = "postgresql://neondb_owner:npg_rtgT9R3GEhAV@ep-snowy-dream-a5reiccc-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# 2. Funções de Banco de Dados
def conectar_banco():
    return psycopg2.connect(DB_URL)

def criar_tabela_se_nao_existir():
    """Cria a tabela no Neon automaticamente caso ela não exista."""
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

def carregar_relatos():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, materia, nivel, detalhes, TO_CHAR(data_envio, 'DD/MM/YYYY HH24:MI') FROM relatos WHERE status = 'Pendente' ORDER BY data_envio DESC")
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    return linhas

def resolver_relato(id_relato):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("UPDATE relatos SET status = 'Resolvido' WHERE id = %s", (id_relato,))
    conn.commit()
    cursor.close()
    conn.close()
    st.rerun()

# Executa a verificação do banco de dados silenciosamente ao iniciar
criar_tabela_se_nao_existir()

# 3. Construção da Interface Principal
st.title("🏫 Painel de Recebimento - Secretaria")
st.markdown("**Sistema ETEC MIND** | Aguardando novos relatos em tempo real...")
st.divider()

relatos = carregar_relatos()

if not relatos:
    st.success("🎉 Parabéns! Nenhum relato pendente no momento.")
else:
    for relato in relatos:
        id_relato, nome, email, materia, nivel, detalhes, data = relato
        
        with st.container(border=True):
            st.subheader(f"📚 {materia} - Dificuldade {nivel}")
            
            texto_email = f"({email})" if email and email != "Não informado" else ""
            st.write(f"**Aluno:** {nome} {texto_email}")
            st.write(f"**Data:** {data}")
            st.warning(detalhes)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if email and email != "Não informado":
                    assunto = urllib.parse.quote(f"ETEC MIND - Retorno sobre seu relato de {materia}")
                    saudacao = f"Olá, {nome}!" if nome != "Anônimo" else "Olá!"
                    mensagem = urllib.parse.quote(f"{saudacao}\n\nA coordenação recebeu o seu relato. Gostaríamos de conversar com você para ajudar.")
                    
                    st.markdown(f"""
                        <a href="mailto:{email}?subject={assunto}&body={mensagem}" 
                           style="background-color:#28a745; color:white; padding:8px 15px; border-radius:5px; text-decoration:none; display:inline-block;">
                           ✉️ Enviar E-mail
                        </a>
                        """, unsafe_allow_html=True)
            
            with col2:
                if st.button("✔ Marcar como Resolvido", key=f"btn_{id_relato}", type="primary"):
                    resolver_relato(id_relato)

# ==========================================
# TRUQUE DEFINITIVO PARA RODAR PELO BOTÃO PLAY
# ==========================================
if __name__ == '__main__':
    if "streamlit" not in sys.argv[0].lower():
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
