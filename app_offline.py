import sys

# Tenta forçar o carregamento do SQLite compatível com o navegador
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime
import os
# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="PreparaCalda Pro ", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO AGRO TECH (CSS) ---
st.markdown("""
    <style>
    /* Fundo e Fontes */
    .main { background-color: #fcfdfc; }
    h1, h2, h3 { color: #1b5e20 !important; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    
    /* Box de Dosagem Personalizada */
    .dosagem-box { 
        border-left: 5px solid #2e7d32; 
        padding: 20px; 
        border-radius: 15px; 
        background-color: #ffffff; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    
    /* Botões estilo Mobile App */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
        color: white !important;
        border: none;
        padding: 15px;
        font-weight: bold;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
        transition: all 0.3s;
    }
    
    /* Ajustes para iPhone (Safe Area) e Android */
    @media (max-width: 768px) {
        .stApp { margin-bottom: 50px; }
        .dosagem-box { padding: 15px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES CORE ---
def conectar_banco():
    return sqlite3.connect('preparacalda2.db')

# --- HEADER DECORATIVO ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    st.markdown("# 🚜")
with col_tit:
    st.title("PreparaCalda Pro")
    st.caption("🛡️ Tecnologia para Rendimento")

# --- VERIFICAÇÃO DE DADOS ---
if not os.path.exists('preparacalda2.db'):
    st.warning("🔄 Sincronizando base de dados... Por favor, aguarde.")
    st.stop()

conn = conectar_banco()

# --- SIDEBAR (HISTÓRICO) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2318/2318283.png", width=80)
    st.header("🕒 Histórico Local")
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS Logs_Consultas (id_log INTEGER PRIMARY KEY AUTOINCREMENT, data_hora TEXT, protocolo_consultado TEXT)")
        df_logs = pd.read_sql("SELECT data_hora, protocolo_consultado FROM Logs_Consultas ORDER BY id_log DESC LIMIT 5", conn)
        for _, log in df_logs.iterrows():
            with st.expander(f"📅 {log['data_hora']}"):
                st.caption(log['protocolo_consultado'])
    except:
        st.info("Nenhuma consulta salva.")

# --- INTERFACE DE CÁLCULO ---
st.markdown("### 📋 1. Planejamento da Calda")
with st.container():
    c1, c2 = st.columns([2, 1])
    with c1:
        try:
            df_p = pd.read_sql("SELECT nome_comercial FROM Produtos ORDER BY nome_comercial", conn)
            selecionados = st.multiselect("Selecione os Insumos:", df_p['nome_comercial'].tolist())
        except:
            st.error("Falha ao carregar lista de produtos.")
            st.stop()
    with c2:
        vol_tanque = st.number_input("Capacidade Tanque (L):", min_value=100, value=2000, step=100)

# --- DOSAGENS ---
dosagens = {}
if selecionados:
    st.markdown("---")
    st.markdown("### ⚖️ 2. Dosagens por Tanque")
    grid = st.columns(2)
    
    for idx, prod in enumerate(selecionados):
        with grid[idx % 2]:
            st.markdown(f'''
                <div class="dosagem-box">
                    <span style="color:#2e7d32; font-size: 0.8em; font-weight: bold;">PRODUTO</span><br>
                    <span style="font-size: 1.2em; font-weight: bold;">{prod}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            if "Progibb" in prod:
                d = st.number_input(f"Sachês / 1000L:", min_value=0.0, step=0.1, key=f"v_{prod}")
                calc = (d / 1000) * vol_tanque
                dosagens[prod] = f"{calc:.2f} sachês"
            else:
                d = st.number_input(f"Dose / 100L (ml ou g):", min_value=0.0, step=10.0, key=f"v_{prod}")
                calc = (d / 100) * vol_tanque
                dosagens[prod] = f"{calc:.2f} unidades"

    # --- PROTOCOLO FINAL ---
    if st.button("🚀 GERAR PROTOCOLO DE PREPARO"):
        st.markdown("---")
        st.markdown("### 📝 Ordem de Adição Segura")
        
        # Alerta de Água (Essencial)
        st.info(f"💧 **PASSO INICIAL:** Abastecer o tanque com **{vol_tanque * 0.5:.0f} Litros** de água e ativar a agitação.")

        # Lógica de Prioridade Químicas
        placeholder = ', '.join(['?'] * len(selecionados))
        query = f"""
            SELECT p.nome_comercial, p.tipo_formulacao, c.nome_categoria 
            FROM Produtos p 
            JOIN Categorias c ON p.id_categoria = c.id_categoria 
            WHERE p.nome_comercial IN ({placeholder}) 
            ORDER BY c.ordem_prioridade ASC
        """
        df_ordem = pd.read_sql(query, conn, params=selecionados)

        for i, r in df_ordem.iterrows():
            with st.expander(f"🔹 {i+1}º: {r['nome_comercial']}", expanded=True):
                col_ic, col_txt = st.columns([1, 4])
                with col_txt:
                    st.markdown(f"**Quantidade:** {dosagens[r['nome_comercial']]}")
                    tipo = (r['tipo_formulacao'] or "").upper()
                    if any(x in tipo for x in ['WP', 'WG', 'SG', 'FERT PO']):
                        st.error(f"⚠️ **SÓLIDO DETECTADO:** Realizar pré-diluição obrigatória.")
                    st.caption(f"Classe: {r['nome_categoria']} | Tipo: {tipo}")

        st.success(f"✅ **FINALIZAÇÃO:** Completar o volume até atingir **{vol_tanque}L**.")
        
        # Log de Segurança
        try:
            agora = datetime.now().strftime("%d/%m - %H:%M")
            conn.execute("INSERT INTO Logs_Consultas (data_hora, protocolo_consultado) VALUES (?, ?)", 
                         (agora, " + ".join(selecionados)))
            conn.commit()
        except: pass


conn.close()

