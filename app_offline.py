import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA (Execução Local) ---
st.set_page_config(
    page_title="PreparaCalda Pro ", 
    page_icon="🚜", 
    layout="wide"
)

# --- FUNÇÃO DE CONEXÃO (Padrão stlite) ---
def conectar_banco():
    """Conecta ao arquivo .db montado virtualmente pelo index.html"""
    return sqlite3.connect('preparacalda2.db')

# --- CSS EMBUTIDO (Evita chamadas de rede para estilo) ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .dosagem-box { 
        border: 2px solid #2e7d32; 
        padding: 15px; 
        border-radius: 12px; 
        background-color: #f1f8e9; 
        margin-bottom: 10px;
    }
    .stButton>button {
        width: 100%;
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        height: 3em;
    }
    /* Estilo para garantir leitura no sol (alto contraste) */
    h1, h2, h3 { color: #1b5e20 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE INICIALIZAÇÃO ---
if not os.path.exists('preparacalda2.db'):
    st.error("⚠️ Banco de dados não encontrado no ambiente virtual.")
    st.info("Verifique se o arquivo 'preparacalda2.db' está listado no index.html")
    st.stop()

conn = conectar_banco()

# --- INTERFACE PRINCIPAL ---
st.title("🚜 PreparaCalda Pro")
st.caption("Versão Offline para Campo")

# --- HISTÓRICO LOCAL (Salvo no cache do navegador) ---
with st.sidebar:
    st.header("🕒 Histórico Recente")
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS Logs_Consultas (id_log INTEGER PRIMARY KEY AUTOINCREMENT, data_hora TEXT, protocolo_consultado TEXT)")
        df_logs = pd.read_sql("SELECT data_hora, protocolo_consultado FROM Logs_Consultas ORDER BY id_log DESC LIMIT 5", conn)
        for _, log in df_logs.iterrows():
            st.markdown(f"**{log['data_hora']}**")
            st.caption(log['protocolo_consultado'])
            st.divider()
    except:
        st.info("O histórico será criado na primeira consulta.")

# --- FORMULÁRIO DE MISTURA ---
st.subheader("1. Configuração da Mistura")
col1, col2 = st.columns([2, 1])

with col1:
    try:
        df_p = pd.read_sql("SELECT nome_comercial FROM Produtos ORDER BY nome_comercial", conn)
        selecionados = st.multiselect("Selecione os produtos:", df_p['nome_comercial'].tolist())
    except Exception as e:
        st.error("Erro ao ler tabela de produtos.")
        st.stop()

with col2:
    vol_tanque = st.number_input("Tanque (Litros):", min_value=100, value=2000)

# --- CÁLCULO DE DOSAGENS ---
dosagens = {}
if selecionados:
    st.subheader("2. Dosagens Necessárias")
    grid = st.columns(2) # Melhor para mobile (2 colunas)
    
    for idx, prod in enumerate(selecionados):
        with grid[idx % 2]:
            st.markdown(f'<div class="dosagem-box">', unsafe_allow_html=True)
            st.markdown(f"**{prod}**")
            
            # Lógica para sachês ou litros
            if "Progibb" in prod:
                d = st.number_input(f"Sachês/1000L:", min_value=0.0, step=0.1, key=f"k_{prod}")
                total = (d / 1000) * vol_tanque
                dosagens[prod] = f"{total:.2f} sachês"
            else:
                d = st.number_input(f"Dose/100L (ml/g):", min_value=0.0, step=10.0, key=f"k_{prod}")
                total = (d / 100) * vol_tanque
                dosagens[prod] = f"{total:.2f} (ml/g)"
            
            st.markdown('</div>', unsafe_allow_html=True)

    # --- GERAÇÃO DO PROTOCOLO ---
    if st.button("GERAR ORDEM DE MISTURA"):
        st.divider()
        st.subheader("📜 Ordem de Preparo")
        
        # Passo 0
        st.warning(f"**Passo 0:** Abasteça **{vol_tanque * 0.5:.0f}L** de água e ligue o agitador.")

        # Busca Prioridades
        query = f"SELECT p.nome_comercial, p.tipo_formulacao, c.nome_categoria FROM Produtos p JOIN Categorias c ON p.id_categoria = c.id_categoria WHERE p.nome_comercial IN ({','.join(['?']*len(selecionados))}) ORDER BY c.ordem_prioridade ASC"
        df_ordem = pd.read_sql(query, conn, params=selecionados)

        for i, r in df_ordem.iterrows():
            with st.container():
                st.success(f"**{i+1}º - {r['nome_comercial']}**")
                st.write(f"Quantidade: **{dosagens[r['nome_comercial']]}**")
                
                # Alerta de Sólidos
                tipo = (r['tipo_formulacao'] or "").upper()
                if any(x in tipo for x in ['WP', 'WG', 'SG', 'FERT PO']):
                    st.error(f"❗ **PRÉ-DILUIÇÃO:** Diluir em balde antes de despejar.")
                
                st.caption(f"Tipo: {tipo} | {r['nome_categoria']}")
                st.divider()

        st.info(f"**Finalização:** Complete o volume para **{vol_tanque}L**.")

        # Salvar Log
        try:
            agora = datetime.now().strftime("%H:%M - %d/%m")
            conn.execute("INSERT INTO Logs_Consultas (data_hora, protocolo_consultado) VALUES (?, ?)", 
                         (agora, " + ".join(selecionados)))
            conn.commit()
        except:
            pass

conn.close()