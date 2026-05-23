import streamlit as st

st.set_page_config(
    page_title="Dashboard Insper One",
    layout="wide"
)

st.image("https://mundologistica.com.br/galeria/1777315848-logo-insper-2.png")

st.title("Dashboard - Desempenho dos alunos do Insper One")

st.markdown("""
Use o menu lateral para navegar entre as páginas:

- **Aluno por aluno**
- **Comparar**
""")