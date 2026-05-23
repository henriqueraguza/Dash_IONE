import pandas as pd
import streamlit as st
import plotly.express as px
st.title("Alunos")

graduacao = pd.read_excel("Dados.xlsx", sheet_name="Graduacao")
one = pd.read_excel("Dados.xlsx", sheet_name="IOne")

# Padronizando nomes das colunas, caso tenha espaços escondidos
graduacao.columns = graduacao.columns.str.strip()
one.columns = one.columns.str.strip()

# Criando nomes limpos para cruzamento
graduacao["Aluno_limpo"] = graduacao["Aluno"].astype(str).str.strip().str.lower()
one["Nome_limpo"] = one["Aluno"].astype(str).str.strip().str.lower()

st.subheader("Filtros")

col_f1, col_f2 = st.columns(2)

with col_f1:
    curso_select = st.selectbox(
        label="Curso",
        options=["Todos"] + sorted(graduacao["CURSO"].dropna().unique().tolist())
    )

with col_f2:
    insper_one_select = st.selectbox(
        label="Insper One",
        options=["Todos"] + sorted(graduacao["Insper One"].dropna().unique().tolist())
    )

# Começa com a base inteira
graduacao_filtrada = graduacao.copy()

if curso_select != "Todos":
    graduacao_filtrada = graduacao_filtrada[
        graduacao_filtrada["CURSO"] == curso_select
    ]

if insper_one_select != "Todos":
    graduacao_filtrada = graduacao_filtrada[
        graduacao_filtrada["Insper One"] == insper_one_select
    ]

nomes_disponiveis = sorted(graduacao_filtrada["Aluno"].dropna().unique().tolist())

if len(nomes_disponiveis) == 0:
    st.warning("Nenhum aluno encontrado com esses filtros.")
    st.stop()

nome_select = st.selectbox(
    label="Nome do Aluno",
    options=nomes_disponiveis
)

linha_nome = graduacao_filtrada[graduacao_filtrada["Aluno"] == nome_select]

nome = linha_nome["Aluno"].iloc[0]
curso = linha_nome["CURSO"].iloc[0]
ione = linha_nome["Insper One"].iloc[0]
matricula = linha_nome["MATRICULA"].iloc[0]
nome_limpo = linha_nome["Aluno_limpo"].iloc[0]

# =========================
# RESUMO DO ALUNO
# =========================

st.subheader("Resumo do aluno")

st.metric("Nome", nome)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Matrícula", matricula)

with col2:
    st.metric("Curso", curso)

with col3:
    st.metric("Insper One", ione)

st.divider()

# =========================
# NOTAS DA GRADUAÇÃO
# =========================

st.subheader("Grade de notas - Graduação")

st.dataframe(
    linha_nome[["DISCIPLINA", "FALTAS", "NOTA FINAL"]],
    use_container_width=True
)

# =========================
# NOTAS DO INSPER ONE
# =========================

if ione == "Sim":
    st.subheader("Notas - Insper One")

    linha_one = one[one["Nome_limpo"] == nome_limpo]

    if len(linha_one) == 0:
        st.warning("O aluno está marcado como Insper One, mas não foi encontrado na aba IONE.")
    else:
        st.dataframe(
            linha_one[['Curso','COMUNICAÇÃO I','COMUNICAÇÃO II','MATEMÁTICA 1','MATEMÁTICA 2','COMPUTAÇÃO','REALIDADE CONTEMPORÂNEA','FÍSICA','FUND. LEITURA JURÍDICA']],
            use_container_width=True
        )
else:
    st.info("Este aluno não está marcado como participante do Insper One.")

st.divider()
st.subheader("Comparação de médias")
# Copia só as colunas necessárias
notas_grad = linha_nome[["DISCIPLINA", "NOTA FINAL"]].copy()

# Garante que NOTA FINAL está como número
notas_grad["NOTA FINAL"] = pd.to_numeric(
    notas_grad["NOTA FINAL"],
    errors="coerce"
)

# Padroniza o nome da disciplina
notas_grad["DISCIPLINA_LIMPA"] = (
    notas_grad["DISCIPLINA"]
    .astype(str)
    .str.upper()
    .str.strip()
)

# Identifica a linha de Tópicos Essenciais
mask_topicos = notas_grad["DISCIPLINA_LIMPA"].str.contains(
    "TÓPICOS ESSENCIAIS|TOPICOS ESSENCIAIS",
    na=False
)

# Pega a nota de Tópicos
nota_topicos = notas_grad.loc[mask_topicos, "NOTA FINAL"]

# Se existir Tópicos e a nota for zero, remove essa linha da média
if len(nota_topicos) > 0 and nota_topicos.iloc[0] == 0:
    notas_para_media = notas_grad[~mask_topicos]
else:
    notas_para_media = notas_grad.copy()

# Calcula a média corretamente
media_graduacao = notas_para_media["NOTA FINAL"].mean()

if ione == "Sim" and len(linha_one) > 0:
    media_one = pd.to_numeric(
        linha_one["MÉDIA FINAL"],
        errors="coerce"
    ).iloc[0]

    medias = pd.DataFrame({
        "Média": [media_graduacao, media_one]
    }, index=["Graduação", "Insper One"])

else:
    medias = pd.DataFrame({
        "Média": [media_graduacao]
    }, index=["Graduação"])

medias_plot = medias.reset_index()
medias_plot.columns = ["Tipo", "Média"]

fig_medias = px.bar(
    medias_plot,
    x="Tipo",
    y="Média",
    color="Tipo",
    text="Média",
    color_discrete_map={
        "Graduação": "#E6002D",   # vermelho
        "Insper One": "#1ABC9C"   # verde
    },
    title="Comparação de médias do aluno",
    labels={
        "Tipo": "",
        "Média": "Média"
    }
)

fig_medias.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig_medias.update_layout(
    template="plotly_white",
    yaxis_range=[0, 10],
    showlegend=False,
    xaxis_title="",
    yaxis_title="Média"
)

st.plotly_chart(fig_medias, use_container_width=True)