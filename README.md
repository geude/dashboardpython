# 🏗️ Controle de Gastos de Construção

Aplicação interativa em **Streamlit** para registrar, organizar e visualizar os gastos de uma construção.  
Permite cadastrar materiais e serviços, visualizar uma lista consolidada, calcular o total gasto e gerar gráficos de análise.

---

## 🚀 Funcionalidades

- ✅ Cadastro de **materiais/serviços** com nome, data e valor.  
- ✅ Tabela consolidada com todos os gastos.  
- ✅ Total geral automaticamente atualizado.  
- ✅ Gráfico de barras horizontal com a distribuição de gastos.  
- ✅ Download da tabela completa em **CSV**.  

---

## 🖥️ Demonstração da Interface

- **Lista de Gastos**: exibida em tabela com rolagem.  
- **Gráfico de Gastos**: barras horizontais mostrando os itens mais caros.  
- **Resumo Total**: métrica com o valor consolidado gasto.  

---

## 📦 Tecnologias Utilizadas

- [Python 3.10+](https://www.python.org/)  
- [Streamlit](https://streamlit.io/)  
- [Pandas](https://pandas.pydata.org/)  
- [Matplotlib](https://matplotlib.org/)  

---

## ⚙️ Instalação e Uso

Clone o repositório:

git clone https://github.com/geude/dashboardpython

Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  'Linux/Mac'
venv\Scripts\activate     'Windows'

Instale as dependências
streamlit run app.py


.
├── app.py                  # Código principal da aplicação
├── orcamento_construcao.csv # Arquivo CSV com os gastos (criado automaticamente)
├── requirements.txt        # Dependências do projeto
└── README.md               # Documentação


Exemplo de Uso

Abra a aplicação: http://localhost:8501

Adicione um novo gasto pela barra lateral.

Veja os dados aparecerem automaticamente na tabela consolidada.

Analise o gráfico para entender quais itens mais impactam no orçamento.

Baixe os dados em CSV para relatórios externos.
