import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

DATA_FILE = 'orcamento_construcao.csv'

# --- Funções ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df['Data'].fillna(pd.Timestamp.today(), inplace=True)
        df['Custo'] = pd.to_numeric(df['Custo'], errors='coerce').fillna(0)
        return df
    else:
        return pd.DataFrame(columns=['Material/Serviço', 'Data', 'Custo'])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- Interface ---
st.title("🏗️ Controle de Construção")
st.markdown("### Controle e Consolidação de Gastos")

# --- Formulário ---
st.sidebar.header("Adicionar Novo Gasto")
nome_item = st.sidebar.text_input("Nome do Material ou Serviço")
valor_gasto = st.sidebar.number_input("Valor do Gasto (R$)", min_value=0.0, format="%.2f")
data_gasto = st.sidebar.date_input("Data da Compra", datetime.today())
adicionar = st.sidebar.button("Adicionar à Lista")

if adicionar:
    if nome_item and valor_gasto > 0:
        df = load_data()
        new_entry = pd.DataFrame([{
            'Material/Serviço': nome_item,
            'Data': pd.to_datetime(data_gasto),
            'Custo': valor_gasto
        }])
        df = pd.concat([new_entry, df], ignore_index=True)
        df = df.sort_values(by="Data", ascending=False)
        save_data(df)
        st.success("Dados adicionados com sucesso!")
    else:
        st.error("Por favor, preencha todos os campos corretamente.")

# --- Exibição de Dados ---
df_hist = load_data()
st.header("Lista de Gastos Consolidados")

if not df_hist.empty:
    df_display = df_hist.copy()
    df_display['Custo'] = df_display['Custo'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    st.dataframe(df_display, hide_index=True, height=200)

    st.markdown("---")

    total_geral = df_hist['Custo'].sum()
    st.metric(
        label="Valor Total Geral Gasto",
        value=f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.subheader("Distribuição dos Gastos por Item")
    gastos_por_item = df_hist.groupby("Material/Serviço")["Custo"].sum().sort_values(ascending=True)  # menor no topo

    # Gráfico de barras horizontal
    fig, ax = plt.subplots(figsize=(8, max(2, len(gastos_por_item)*0.5)))  # altura dinâmica
    ax.barh(gastos_por_item.index, gastos_por_item.values, color='skyblue')
    ax.set_xlabel("Valor (R$)")
    ax.set_ylabel("Material / Serviço")
    ax.set_title("Gastos Consolidados por Item")
    for i, v in enumerate(gastos_por_item.values):
        ax.text(v + max(gastos_por_item.values)*0.01, i, f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                va='center')
    st.pyplot(fig)

    st.markdown("### 📥 Baixar Relatório")
    csv_data = df_hist.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Baixar tabela em CSV",
        data=csv_data,
        file_name="orcamento_construcao.csv",
        mime="text/csv",
    )
else:
    st.info("Nenhum dado de gasto registrado ainda.")