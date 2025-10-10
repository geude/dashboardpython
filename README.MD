## 🚀 Funcionalidades

- 🗑️ **Exclusão de registros por ID** — controle total dos dados cadastrados.  
- 📆 **Previsão de gastos** — estimativas **semanais e mensais** baseadas em histórico.  
- 📊 **Gráfico de evolução temporal** — visualização da tendência de despesas ao longo do tempo.  
- 📈 **Estatísticas detalhadas:**
  - Quantidade total de itens.
  - Valor médio por item.
  - Período analisado automaticamente.  

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Descrição |
|-------------|------------|
| **Python 3.12+** | Linguagem principal |
| **Streamlit** | Criação do dashboard interativo |
| **Pandas** | Manipulação e análise de dados |
| **Matplotlib / Plotly** | Visualização gráfica |
| **Scikit-learn (opcional)** | Modelagem preditiva para projeções de gastos |

---


## ⚙️ Como Executar Localmente

1. **Clone este repositório:**
   ```bash
   git clone https://github.com/geude/dashboardpython.git
   cd dashboardpython

# Crie um ambiente virtual

python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# Instale as dependências

pip install -r requirements.txt

# Execute o dashaboard

streamlit run app.py

Exemplo de uso

- Adicione novos registros de despesas com descrição, data e valor.

- Visualize automaticamente gráficos e estatísticas.

- Consulte previsões futuras de gastos semanais e mensais.

- Exclua lançamentos por ID para manter a base de dados organizada.



