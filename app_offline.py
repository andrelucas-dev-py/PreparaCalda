import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="PreparaCalda Pro", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO AGRO TECH (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #fcfdfc; }
    h1, h2, h3 { color: #1b5e20 !important; font-family: 'Segoe UI', sans-serif; }
    
    .dosagem-box { 
        border-left: 5px solid #2e7d32; 
        padding: 20px; 
        border-radius: 15px; 
        background-color: #ffffff; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
        color: white !important;
        border: none;
        padding: 15px;
        font-weight: bold;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS (CSV substitui SQL) ---
@st.cache_data
def carregar_base_dados():
    if os.path.exists('produtos.csv') and os.path.exists('categorias.csv'):
        df_p = pd.read_csv('produtos.csv')
        df_c = pd.read_csv('categorias.csv')
        # Faz o JOIN via Pandas
        return pd.merge(df_p, df_c, on='id_categoria')
    return None

# --- HEADER ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    st.markdown("# 🚜")
with col_tit:
    st.title("PreparaCalda Pro")
    st.caption("🛡️ Tecnologia para Rendimento (Versão Offline-Web)")

df_completo = carregar_base_dados()

if df_completo is None:
    st.warning("🔄 Sincronizando arquivos de dados... Por favor, aguarde.")
    st.stop()

# --- INTERFACE DE CÁLCULO ---
st.markdown("### 📋 1. Planejamento da Calda")
with st.container():
    c1, c2 = st.columns([2, 1])
    with c1:
        # Pega lista única de produtos do CSV
        lista_produtos = sorted(df_completo['nome_comercial'].unique())
        selecionados = st.multiselect("Selecione os Insumos:", lista_produtos)
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
            
            # Lógica de cálculo conforme seu original
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
        
        st.info(f"💧 **PASSO INICIAL:** Abastecer o tanque com **{vol_tanque * 0.5:.0f} Litros** de água e ativar a agitação.")

        # FILTRAGEM E ORDENAÇÃO (Substitui o ORDER BY do SQL)
        df_ordem = df_completo[df_completo['nome_comercial'].isin(selecionados)].copy()
        df_ordem = df_ordem.sort_values(by='ordem_prioridade', ascending=True)

        for i, row in enumerate(df_ordem.itertuples(), 1):
            with st.expander(f"🔹 {i}º: {row.nome_comercial}", expanded=True):
                st.markdown(f"**Quantidade:** {dosagens[row.nome_comercial]}")
                tipo = (str(row.tipo_formulacao)).upper()
                
                # Alerta de Sólidos
                if any(x in tipo for x in ['WP', 'WG', 'SG', 'PO']):
                    st.error(f"⚠️ **SÓLIDO DETECTADO:** Realizar pré-diluição obrigatória.")
                
                st.caption(f"Classe: {row.nome_categoria} | Tipo: {tipo}")

        st.success(f"✅ **FINALIZAÇÃO:** Completar o volume até atingir **{vol_tanque}L**.")

# Removido Histórico em SQL para evitar erros de escrita no navegador.
# Dica: Você pode usar st.session_state se quiser um histórico temporário.



