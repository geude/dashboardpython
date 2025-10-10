import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np 
from prophet import Prophet 

# --- CONSTANTES ---
DATA_FILE = 'orcamento_construcao.csv'

# --- INICIALIZAÇÃO DE ESTADO ---
if 'nome_material_input' not in st.session_state:
    st.session_state.nome_material_input = ""
if 'valor_gasto_input' not in st.session_state:
    st.session_state.valor_gasto_input = 0.0

# --- FUNÇÕES DE DADOS (CRUD) ---

def load_data():
    """Carrega dados do CSV com tratamento robusto de erros."""
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            
            # Verifica se as colunas necessárias existem
            required_cols = ['Material/Serviço', 'Data', 'Custo']
            if not all(col in df.columns for col in required_cols):
                st.error("Estrutura do arquivo CSV inválida")
                return pd.DataFrame(columns=['ID', 'Material/Serviço', 'Data', 'Custo'])
            
            # Garantir que todas as datas sejam datetime
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            df['Custo'] = pd.to_numeric(df['Custo'], errors='coerce').fillna(0)
            
            # Remove linhas com datas inválidas
            df = df[df['Data'].notna()].copy()
            
            df['ID'] = range(1, len(df)+1)
            return df
            
        except Exception as e:
            st.error(f"Erro ao carregar arquivo: {e}")
            return pd.DataFrame(columns=['ID', 'Material/Serviço', 'Data', 'Custo'])
    else:
        return pd.DataFrame(columns=['ID', 'Material/Serviço', 'Data', 'Custo'])

def save_data(df):
    """Salva o DataFrame no CSV."""
    try:
        # Salvar datas no formato ISO para evitar problemas
        df_to_save = df.copy()
        df_to_save['Data'] = df_to_save['Data'].dt.strftime('%Y-%m-%d')
        df_to_save.to_csv(DATA_FILE, index=False)
    except Exception as e:
        st.error(f"Erro ao salvar arquivo: {e}")

def excluir_linha(df, id_alvo):
    """Exclui uma linha usando ID e recalcula os IDs sequencialmente."""
    if id_alvo not in df['ID'].values:
        st.error(f"Erro: ID {id_alvo} não encontrado.")
        return df
    
    df = df[df['ID'] != id_alvo].copy()
    
    if not df.empty:
        df['ID'] = range(1, len(df) + 1)
    
    save_data(df)
    st.success(f"Linha ID {id_alvo} excluída com sucesso.")
    return df

# --- FUNÇÕES DE PREVISÃO ---

def prepare_data_for_prophet(df, freq):
    """Prepara o DataFrame agregando por frequência com tratamento melhorado."""
    df_ts = df.dropna(subset=['Data', 'Custo']).copy()
    
    if len(df_ts) < 2:
        return pd.DataFrame()
    
    df_ts['Data'] = pd.to_datetime(df_ts['Data'])
    
    if freq == 'MENSAL':
        df_aggregated = df_ts.set_index('Data')['Custo'].resample('MS').sum().reset_index()
    else: 
        df_aggregated = df_ts.set_index('Data')['Custo'].resample('W-MON').sum().reset_index()

    df_aggregated.columns = ['ds', 'y']
    
    if len(df_aggregated) > 0:
        if df_aggregated['y'].sum() == 0:
            media_geral = df_ts['Custo'].mean()
            df_aggregated['y'] = media_geral
        else:
            media_valores = df_aggregated[df_aggregated['y'] > 0]['y'].mean()
            df_aggregated['y'] = df_aggregated['y'].replace(0, media_valores)
    
    return df_aggregated

def run_prophet_forecast(df_prophet, periods, freq):
    if len(df_prophet) < 5:
        return None

    try:
        m = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=(freq == 'SEMANAL'),
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=0.01,
            seasonality_mode='additive'
        )
        
        m.fit(df_prophet)
        prophet_freq = 'M' if freq == 'MENSAL' else 'W'
        future = m.make_future_dataframe(periods=periods, freq=prophet_freq, include_history=True)
        forecast = m.predict(future)
        return forecast, m
        
    except Exception as e:
        st.error(f"Erro no Prophet: {e}")
        return None

def create_forecast_plot(df_hist, forecast, freq):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_hist['ds'], df_hist['y'], 'bo-', label='Dados Históricos', markersize=4)
    future_forecast = forecast[forecast['ds'] > df_hist['ds'].max()]
    
    if len(future_forecast) > 0:
        ax.plot(future_forecast['ds'], future_forecast['yhat'], 'r-', label='Previsão', linewidth=2)
        ax.fill_between(future_forecast['ds'], future_forecast['yhat_lower'], future_forecast['yhat_upper'], 
                       alpha=0.2, color='red', label='Intervalo de Confiança')
    
    ax.set_xlabel('Data')
    ax.set_ylabel('Custo (R$)')
    ax.set_title(f'Previsão de Gastos - {freq.title()}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def get_next_period_forecast(forecast, df_hist, freq):
    if forecast is None or len(forecast) == 0:
        return 0.0
    
    last_historical_date = df_hist['ds'].max()
    future_forecast = forecast[forecast['ds'] > last_historical_date]
    
    if len(future_forecast) == 0:
        return 0.0
    
    next_period = future_forecast.iloc[0]
    return max(0.0, next_period['yhat'])

def formatar_moeda(valor):
    if pd.isna(valor) or valor == 0:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- INTERFACE PRINCIPAL ---
st.title("🏗️ Controle de Construção")

# --- Lógica de Adição (Sidebar) ---
st.sidebar.header("Adicionar Novo Gasto")
nome_item = st.sidebar.text_input("Nome do Material ou Serviço")
valor_gasto = st.sidebar.number_input("Valor do Gasto (R$)", min_value=0.0, format="%.2f")
data_gasto = st.sidebar.date_input("Data da Compra", datetime.today())

if st.sidebar.button("Adicionar à Lista"):
    if nome_item and valor_gasto > 0:
        df = load_data()
        new_entry = pd.DataFrame([{
            'Material/Serviço': nome_item,
            'Data': pd.to_datetime(data_gasto),
            'Custo': valor_gasto
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.sort_values(by="Data", ascending=False).reset_index(drop=True)
        df['ID'] = range(1, len(df) + 1)
        save_data(df)
        st.sidebar.success("Dados adicionados com sucesso!")
        st.rerun()
    else:
        st.sidebar.error("Por favor, preencha todos os campos corretamente.")

# --- CARREGA E EXIBE DADOS ---
df_hist_data = load_data()
st.header("📋 Lista de Gastos Consolidados")

if not df_hist_data.empty:
    df_display = df_hist_data.copy()
    df_display['Data'] = pd.to_datetime(df_display['Data']).dt.strftime('%d/%m/%Y')
    df_display['Custo'] = df_display['Custo'].apply(formatar_moeda)
    
    # Mostrar tabela com todas as colunas
    st.dataframe(df_display[['ID', 'Material/Serviço', 'Data', 'Custo']], hide_index=True, use_container_width=True)

    st.markdown("---")
    total_geral = df_hist_data['Custo'].sum()
    st.metric(label="Valor Total Geral Gasto", value=formatar_moeda(total_geral))

    # Gráfico de distribuição
    st.subheader("📊 Distribuição dos Gastos por Item")
    gastos_por_item = df_hist_data.groupby("Material/Serviço")["Custo"].sum().sort_values(ascending=True)
    if not gastos_por_item.empty:
        cores = ["#000000", "#121312", "#111312", "#131413", "#111B14", "#1D332C", "#182522", "#182E25", "#102019" ,"#0A1607", "#02110B", "#05180D", "#0B2910", "#072517", '#5D606E']
        fig, ax = plt.subplots(figsize=(8, max(3, len(gastos_por_item)*0.4)))
        bars = ax.barh(gastos_por_item.index, gastos_por_item.values, color=cores[:len(gastos_por_item)])
        ax.set_xlabel("Valor (R$)")
        ax.set_title("Gastos Consolidados por Item")
        for i, v in enumerate(gastos_por_item.values):
            ax.text(v + max(gastos_por_item.values)*0.01, i, formatar_moeda(v), va='center', fontsize=9)
        st.pyplot(fig)
    
    # Previsões
    st.subheader("🔮 Previsão de Gastos")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Previsão Semanal")
        df_semanal = prepare_data_for_prophet(df_hist_data, 'SEMANAL')
        if len(df_semanal) >= 5:
            resultado = run_prophet_forecast(df_semanal, 2, 'SEMANAL')
            if resultado:
                forecast, model = resultado
                valor_previsto = get_next_period_forecast(forecast, df_semanal, 'SEMANAL')
                st.metric(label="Próxima Semana", value=formatar_moeda(valor_previsto))
                fig_semanal = create_forecast_plot(df_semanal, forecast, 'Semanal')
                st.pyplot(fig_semanal)
            else:
                st.warning("Não foi possível gerar previsão semanal")
        else:
            semanas_faltantes = 5 - len(df_semanal)
            st.warning(f"⏳ Aguardando mais {semanas_faltantes} semana(s)")

    with col2:
        st.markdown("##### Previsão Mensal")
        df_mensal = prepare_data_for_prophet(df_hist_data, 'MENSAL')
        if len(df_mensal) >= 5:
            resultado = run_prophet_forecast(df_mensal, 1, 'MENSAL')
            if resultado:
                forecast, model = resultado
                valor_previsto = get_next_period_forecast(forecast, df_mensal, 'MENSAL')
                st.metric(label="Próximo Mês", value=formatar_moeda(valor_previsto))
                fig_mensal = create_forecast_plot(df_mensal, forecast, 'Mensal')
                st.pyplot(fig_mensal)
            else:
                st.warning("Não foi possível gerar previsão mensal")
        else:
            meses_faltantes = 5 - len(df_mensal)
            st.warning(f"⏳ Aguardando mais {meses_faltantes} mês(es)")

    # Exclusão
    st.sidebar.subheader("🗑️ Excluir Registro")
    if not df_hist_data.empty:
        id_alvo = st.sidebar.selectbox("Selecione o ID para excluir:", options=df_hist_data['ID'].tolist())
        if st.sidebar.button("Excluir Registro", type="secondary"):
            df_hist_data = excluir_linha(df_hist_data, id_alvo)
            st.rerun()

# --- ESTATÍSTICAS ADICIONAIS ---
if not df_hist_data.empty:
    st.subheader("📈 Estatística Detalhada")
    
    col1, col2, col3 = st.columns(3)
    
    with col2:
        media_mensal = df_hist_data['Custo'].mean()
        st.metric("Média por Item", formatar_moeda(media_mensal))
    
    with col1:
        total_itens = len(df_hist_data)
        st.metric("Total de Itens", total_itens)
    
    with col3:
        if len(df_hist_data) > 1:
            data_inicio = df_hist_data['Data'].min()
            data_fim = df_hist_data['Data'].max()
            dias_total = (data_fim - data_inicio).days + 1
            st.metric("Período Analisado", f"{dias_total} dias")
    
    # Gráfico de evolução temporal
    st.subheader("📈 Evolução Temporal dos Gastos")
    df_temporal = df_hist_data.copy()
    df_temporal['Data'] = pd.to_datetime(df_temporal['Data'])
    df_temporal = df_temporal.sort_values('Data')
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_temporal['Data'], df_temporal['Custo'].cumsum(), 'g-', linewidth=2, label='Gasto Acumulado')
    ax.set_xlabel('Data')
    ax.set_ylabel('Gasto Acumulado (R$)')
    ax.set_title('Evolução do Gasto Total ao Longo do Tempo')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
  
    # Download formatado para impressão
    st.markdown("### 📥 Baixar Relatório para Impressão")
    
    # Criar DataFrame formatado para impressão
    df_impressao = df_hist_data.copy()
    df_impressao['Data'] = pd.to_datetime(df_impressao['Data']).dt.strftime('%d/%m/%Y')
    df_impressao['Custo'] = df_impressao['Custo'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    # Remover coluna ID para impressão
    df_impressao = df_impressao[['Material/Serviço', 'Data', 'Custo']]
    
    # Gerar CSV formatado
    csv_data = df_impressao.to_csv(index=False, sep=';').encode("utf-8-sig")
    st.download_button(
        label="📄 Baixar Relatório", 
        data=csv_data, 
        file_name="relatorio_gastos_construcao.csv", 
        mime="text/csv",
        help="Baixe o relatório para impressão"
    )
    
else:
    st.info("📝 Nenhum gasto registrado. Use o menu lateral para adicionar o primeiro registro.")

