@echo off
REM Este arquivo abre o Dashboard de Orçamento (versão de venda) no navegador

cd /d "%~dp0"
python -m streamlit run dashboard_venda.py
exit
