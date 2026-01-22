import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gestão de Calda - Uva & Manga", 
    page_icon="🍇", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO AGRO-PROFISSIONAL (UVA E MANGA) ---
st.markdown("""
    <style>
    /* Cores voltadas para o Agro: Verde Oliva e Cinza Solo */
    .main { background-color: #f4f7f1; }
    
    h1, h2, h3 { color: #2e5a27 !important; font-family: 'Segoe UI', Arial, sans-serif; }
    
    /* Cartões de Insumos (Estilo Ficha de Campo) */
    .insumo-card { 
        border-left: 10px solid #558b2f; 
        padding: 18px; 
        border-radius: 8px; 
        background-color: #ffffff; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }
    
    /* Botão de Ação Forte */
    .stButton>button {
        width: 100%;
        background-color: #33691e;
        color: white !important;
        border: none;
        padding: 12px;
        font-weight: bold;
        font-size: 1.1em;
        border-radius: 5px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
    }
    .stButton>button:hover { background-color: #558b2f; border: none; }

    /* Estilo do Protocolo Final */
    .passo-box {
        background-color: #ffffff;
        border: 1px solid #c5e1a5;
        padding: 15px;
        border-radius: 10px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE UNIDADES (ML/G) ---
def obter_unidade(formula):
    f = str(formula).upper()
    if any(x in f for x in ['WG', 'WP', 'SG', 'GR', 'PO', 'SÓLIDO']):
        return "g"
    if "SACHÊ" in f:
        return "sachês"
    return "ml"

# --- CARREGAMENTO ---
@st.cache_data
def carregar_base():
    if os.path.exists('produtos.csv') and os.path.exists('categorias.csv'):
        df_p = pd.read_csv('produtos.csv')
        df_c = pd.read_csv('categorias.csv')
        return pd.merge(df_p, df_c, on='id_categoria')
    return None

# --- CABEÇALHO ---
st.markdown("<h1 style='text-align: center;'>🍇 PreparaCalda: Uva e Manga 🥭</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #558b2f;'><b>Controle de Ordem de Adição e Dosagem de Precisão</b></p>", unsafe_allow_html=True)

df = carregar_base()

if df is None:
    st.warning("Aguardando carregamento da base de dados (CSV)...")
    st.stop()

# --- ÁREA DE SELEÇÃO ---
with st.expander("📋 Configurar Tanque e Defensivos", expanded=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        insumos = sorted(df['nome_comercial'].unique())
        selecionados = st.multiselect("Selecione os Produtos da Mistura:", insumos)
    with col2:
        vol_tanque = st.number_input("Volume do Tanque (Litros):", min_value=100, value=2000, step=100)

# --- DOSAGENS ---
dosagens = {}
if selecionados:
    st.subheader("⚖️ Ajuste de Dosagens (Dose por 100L)")
    grid = st.columns(2)
    
    for idx, prod in enumerate(selecionados):
        info = df[df['nome_comercial'] == prod].iloc[0]
        unidade = obter_unidade(info['tipo_formulacao'])
        
        with grid[idx % 2]:
            st.markdown(f'''
                <div class="insumo-card">
                    <small style="color: #689f38;">{info['nome_categoria']}</small><br>
                    <strong>{prod}</strong> ({info['tipo_formulacao']})
                </div>
            ''', unsafe_allow_html=True)
            
            if "PROGIBB" in prod.upper():
                d = st.number_input(f"Dose (Sachês / 1000L):", min_value=0.0, step=0.1, key=f"v_{prod}")
                calc = (d / 1000) * vol_tanque
                dosagens[prod] = f"{calc:,.2f} sachês"
            else:
                d = st.number_input(f"Dose por 100L ({unidade}):", min_value=0.0, step=1.0, key=f"v_{prod}")
                calc = (d / 100) * vol_tanque
                dosagens[prod] = f"{calc:,.2f} {unidade}"

    # --- RESULTADO FINAL ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📝 GERAR PROTOCOLO DE MISTURA"):
        st.markdown("---")
        st.markdown("### 🚜 Protocolo de Abastecimento Segura")
        
        # Orientação Técnica
        st.success(f"**1º Passo:** Encher o tanque com **{vol_tanque * 0.5:.0f}L** de água e ligar o **Agitador**.")

        # Ordenação por Categoria
        df_ordem = df[df['nome_comercial'].isin(selecionados)].copy()
        df_ordem = df_ordem.sort_values(by='ordem_prioridade')

        for i, row in enumerate(df_ordem.itertuples(), 1):
            with st.container():
                st.markdown(f"""
                <div class="passo-box">
                    <span style="color:#33691e; font-weight:bold;">{i}º PRODUTO: {row.nome_comercial}</span><br>
                    <span style="font-size:1.2em;">Quantidade: <b>{dosagens[row.nome_comercial]}</b></span><br>
                    <small>Formulação: {row.tipo_formulacao} | Categoria: {row.nome_categoria}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Alerta de pré-diluição
                if obter_unidade(row.tipo_formulacao) == "g":
                    st.warning(f"⚠️ **Atenção:** Realizar pré-diluição em balde antes de colocar no tanque.")

        st.info(f"**Conclusão:** Completar para **{vol_tanque}L** e manter o agitador até o final da aplicação.")
