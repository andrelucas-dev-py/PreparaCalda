import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PreparaCalda Pro", page_icon="🚜", layout="wide")

def conectar_banco():
    """Estabelece conexão com o banco de dados SQLite local ao navegador."""
    # O stlite monta o arquivo na raiz, então usamos apenas o nome
    return sqlite3.connect('preparacalda2.db')

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    .dosagem-box { 
        border: 1px solid #e6e6e6; 
        padding: 15px; 
        border-radius: 10px; 
        background-color: #f9f9f9; 
        margin-bottom: 10px; 
        min-height: 160px;
    }
    .stAlert { margin-top: 10px; }
    /* Ajuste para telas pequenas (iPhone) */
    @media (max-width: 600px) {
        .dosagem-box { min-height: auto; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚜 PreparaCalda Pro")
st.subheader("Cálculo de Dosagem e Ordem de Mistura")

# --- VERIFICAÇÃO DE SEGURANÇA DO BANCO ---
if not os.path.exists('preparacalda2.db'):
    st.error("Aguarde... Carregando base de dados local.")
    st.stop()

# --- INICIALIZAÇÃO DA CONEXÃO ---
try:
    conn = conectar_banco()
except Exception as e:
    st.error(f"Erro ao conectar ao banco virtual: {e}")
    st.stop()

# --- SIDEBAR: HISTÓRICO DE CONSULTAS ---
st.sidebar.header("🕒 Últimas Consultas")
try:
    # Criar tabela de logs caso não exista (importante para o primeiro uso offline)
    conn.execute("CREATE TABLE IF NOT EXISTS Logs_Consultas (id_log INTEGER PRIMARY KEY AUTOINCREMENT, data_hora TEXT, protocolo_consultado TEXT)")
    
    df_logs = pd.read_sql("SELECT data_hora, protocolo_consultado FROM Logs_Consultas ORDER BY id_log DESC LIMIT 5", conn)
    for _, log in df_logs.iterrows():
        st.sidebar.write(f"📅 **{log['data_hora']}**")
        st.sidebar.caption(f"{log['protocolo_consultado']}")
        st.sidebar.markdown("---")
except:
    st.sidebar.info("O histórico aparecerá aqui após a primeira consulta.")

# --- ÁREA DE INPUT ---
with st.container():
    st.info("### 1. Configuração da Calda")
    col_a, col_b = st.columns(2)
    
    with col_a:
        query_produtos = "SELECT nome_comercial FROM Produtos ORDER BY nome_comercial"
        df_produtos = pd.read_sql(query_produtos, conn)
        
        selecionados = st.multiselect(
            "Selecione os produtos da mistura:",
            options=df_produtos['nome_comercial'].tolist(),
            help="Selecione os itens para ver a ordem correta."
        )
    
    with col_b:
        volume_tanque = st.number_input("Volume do tanque (Litros):", min_value=1, value=2000, step=100)

# --- DOSAGENS DINÂMICAS ---
dosagens_input = {}

if selecionados:
    st.write("### 2. Informe as Dosagens")
    # Colunas responsivas: 3 em PC, 1 em celular (Streamlit cuida disso)
    cols = st.columns(len(selecionados) if len(selecionados) < 4 else 3)
    
    for i, produto in enumerate(selecionados):
        with cols[i % len(cols)]:
            st.markdown(f'<div class="dosagem-box">', unsafe_allow_html=True)
            st.write(f"**{produto}**")
            
            if "Progibb" in produto:
                st.caption("Fórmula: Sachê (2,5g)")
                saches_por_1000 = st.number_input(f"Sachês p/ 1000L:", min_value=0.0, step=0.5, key=f"ds_{produto}")
                total = (saches_por_1000 / 1000) * volume_tanque
                dosagens_input[produto] = f"{total:.2f} sachês totais"
            else:
                dose_100l = st.number_input(f"Dose p/ 100L (ml/g):", min_value=0.0, step=10.0, key=f"ds_{produto}")
                total = (dose_100l / 100) * volume_tanque
                dosagens_input[produto] = f"{total:.2f} (ml/g) totais"
            
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Gerar Protocolo Final"):
        st.markdown("---")
        st.write("### 📜 Protocolo Passo a Passo")
        
        # Passo 0: Água
        st.warning(f"**PASSO 0:** Encha o tanque com **{volume_tanque * 0.5:.0f}L** de água e ligue a agitação.")

        # Passo 1 em diante: Produtos
        placeholder = ', '.join(['?'] * len(selecionados))
        query_ordem = f"""
            SELECT p.nome_comercial, p.tipo_formulacao, c.nome_categoria, c.ordem_prioridade
            FROM Produtos p
            JOIN Categorias c ON p.id_categoria = c.id_categoria
            WHERE p.nome_comercial IN ({placeholder})
            ORDER BY c.ordem_prioridade ASC
        """
        df_res = pd.read_sql(query_ordem, conn, params=selecionados)
        
        for idx, row in df_res.iterrows():
            nome = row['nome_comercial']
            tipo = (row['tipo_formulacao'] or "").upper()
            
            with st.expander(f"Passo {idx+1}: {nome}", expanded=True):
                st.success(f"**Adicionar {dosagens_input[nome]}**")
                if any(x in tipo for x in ['WP', 'WG', 'SG', 'PÓ', 'FERT PO']):
                    st.error(f"⚠️ **PRÉ-DILUIÇÃO OBRIGATÓRIA:** Produto sólido ({tipo}).")
                st.caption(f"Categoria: {row['nome_categoria']}")

        st.info(f"**PASSO FINAL:** Complete até **{volume_tanque}L** com água.")

        # Log
        try:
            data_at = datetime.now().strftime("%d/%m/%Y %H:%M")
            conn.execute("INSERT INTO Logs_Consultas (data_hora, protocolo_consultado) VALUES (?, ?)", 
                         (data_at, " + ".join(selecionados)))
            conn.commit()
            st.toast("Salvo no histórico!")
        except:
            pass

conn.close()