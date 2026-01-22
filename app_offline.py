import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="PreparaCalda Pro", 
    page_icon="🛰️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO HI-TECH AGRO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    .main { background-color: #0e1117; }
    
    /* Títulos e Textos */
    h1, h2, h3 { color: #00e676 !important; font-family: 'Segoe UI', sans-serif; letter-spacing: -1px; }
    p, span, label { color: #e0e0e0 !important; }

    /* Cards de Insumos */
    .dosagem-box { 
        border: 1px solid #1b5e20;
        border-left: 8px solid #00e676; 
        padding: 20px; 
        border-radius: 12px; 
        background-color: #161b22; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        margin-bottom: 15px;
        transition: transform 0.3s;
    }
    .dosagem-box:hover { transform: translateY(-5px); border-color: #00e676; }
    
    /* Botão Futurista */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1b5e20 0%, #00e676 100%);
        color: white !important;
        border: none;
        padding: 18px;
        font-weight: 800;
        text-transform: uppercase;
        border-radius: 8px;
        letter-spacing: 2px;
        transition: all 0.4s;
    }
    .stButton>button:hover { box-shadow: 0 0 25px rgba(0, 230, 118, 0.5); transform: scale(1.02); }

    /* Inputs Personalizados */
    .stNumberInput input { background-color: #0d1117 !important; color: #00e676 !important; border: 1px solid #30363d !important; }
    
    /* Badge de Status */
    .status-badge {
        background: #1b5e20;
        color: #00e676;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.7em;
        font-weight: bold;
        border: 1px solid #00e676;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE UNIDADES ---
def formatar_dosagem(valor, formula):
    form = str(formula).upper()
    if any(x in form for x in ['WG', 'WP', 'SG', 'GR', 'PO']):
        return f"{valor:,.2f} g"
    if "SACHÊ" in form:
        return f"{valor:,.2f} sachês"
    return f"{valor:,.2f} ml"

# --- CARREGAMENTO ---
@st.cache_data
def carregar_base_dados():
    if os.path.exists('produtos.csv') and os.path.exists('categorias.csv'):
        df_p = pd.read_csv('produtos.csv')
        df_c = pd.read_csv('categorias.csv')
        return pd.merge(df_p, df_c, on='id_categoria')
    return None

# --- HEADER TECH ---
c_logo, c_tit = st.columns([1, 5])
with c_logo:
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>📡</h1>", unsafe_allow_html=True)
with c_tit:
    st.markdown("<h1 style='margin-bottom: 0;'>PRECISION CALDA 4.0</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #00e676; font-weight: bold;'>SISTEMA DE GESTÃO DE MISTURAS QUÍMICAS</p>", unsafe_allow_html=True)

df_completo = carregar_base_dados()

if df_completo is None:
    st.info("🧬 Inicializando Kernel... Sincronizando dados de campo.")
    st.stop()

# --- ABA DE PLANEJAMENTO ---
st.markdown("### 🛠️ CONFIGURAÇÃO DA OPERAÇÃO")
with st.container():
    c1, c2 = st.columns([2, 1])
    with c1:
        lista_produtos = sorted(df_completo['nome_comercial'].unique())
        selecionados = st.multiselect("🔍 BUSCAR INSUMOS NO DATABASE:", lista_produtos)
    with c2:
        vol_tanque = st.number_input("💧 CAPACIDADE DO TANQUE (L):", min_value=100, value=2000, step=100)

# --- CALIBRAGEM DE DOSAGENS ---
dosagens = {}
if selecionados:
    st.markdown("---")
    st.markdown("### 🧪 CALIBRAGEM DE FLUXO")
    grid = st.columns(2)
    
    for idx, prod in enumerate(selecionados):
        # Pegar info do produto para decidir a unidade
        info_prod = df_completo[df_completo['nome_comercial'] == prod].iloc[0]
        formulacao = str(info_prod['tipo_formulacao']).upper()

        with grid[idx % 2]:
            st.markdown(f'''
                <div class="dosagem-box">
                    <span class="status-badge">{formulacao}</span><br>
                    <span style="font-size: 1.3em; font-weight: bold; color: #ffffff;">{prod}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            if "PROGIBB" in prod.upper():
                d = st.number_input(f"Sachês / 1000L:", min_value=0.0, step=0.1, key=f"v_{prod}")
                calc = (d / 1000) * vol_tanque
                dosagens[prod] = f"{calc:.2f} sachês"
            else:
                label_unid = "Dose / 100L (g):" if any(x in formulacao for x in ['WG', 'WP', 'PO']) else "Dose / 100L (ml):"
                d = st.number_input(label_unid, min_value=0.0, step=10.0, key=f"v_{prod}")
                calc = (d / 100) * vol_tanque
                dosagens[prod] = formatar_dosagem(calc, formulacao)

    # --- EXECUÇÃO FINAL ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ GERAR PROTOCOLO DE SEQUENCIAMENTO"):
        st.markdown("---")
        st.markdown("### 📑 PROTOCOLO OPERACIONAL PADRÃO (POP)")
        
        st.info(f"💾 **ETAPA 01:** Abastecimento primário: **{vol_tanque * 0.5:.0f}L H2O** | Sistema de agitação: **ATIVADO**")

        df_ordem = df_completo[df_completo['nome_comercial'].isin(selecionados)].copy()
        df_ordem = df_ordem.sort_values(by='ordem_prioridade', ascending=True)

        for i, row in enumerate(df_ordem.itertuples(), 1):
            with st.expander(f"📦 PASSO {i:02d}: {row.nome_comercial}", expanded=True):
                c_data, c_warn = st.columns([3, 2])
                with c_data:
                    st.markdown(f"**VOLUME TOTAL:** <span style='font-size: 1.5em; color: #00e676;'>{dosagens[row.nome_comercial]}</span>", unsafe_allow_html=True)
                    st.caption(f"CLASSE: {row.nome_categoria} | QUÍMICA: {row.tipo_formulacao}")
                with c_warn:
                    if any(x in str(row.tipo_formulacao).upper() for x in ['WP', 'WG', 'FERT PO']):
                        st.warning("☣️ REQUER PRÉ-DILUIÇÃO")
                    else:
                        st.success("✅ ADIÇÃO DIRETA")

        st.success(f"🏁 **CONCLUSÃO:** Completar volume final para **{vol_tanque}L** | Manter recirculação ativa.")
