import pandas as pd
import streamlit as st
import plotly.express as px
from scipy import stats

st.title("Comparação de Médias")

graduacao = pd.read_excel("Dados.xlsx", sheet_name="Graduacao")

graduacao.columns = graduacao.columns.str.strip()

# =========================
# FILTRO DE CURSO
# =========================

st.subheader("Filtros")

curso_select = st.selectbox(
    label="Curso",
    options=["Todos"] + sorted(graduacao["CURSO"].dropna().unique().tolist())
)

graduacao_filtrada = graduacao.copy()

if curso_select != "Todos":
    graduacao_filtrada = graduacao_filtrada[
        graduacao_filtrada["CURSO"] == curso_select
    ]

# =========================
# TRATAMENTO DAS NOTAS
# =========================

graduacao_filtrada["NOTA FINAL"] = pd.to_numeric(
    graduacao_filtrada["NOTA FINAL"].astype(str).str.replace(",", ".", regex=False),
    errors="coerce"
)

graduacao_filtrada["DISCIPLINA_LIMPA"] = (
    graduacao_filtrada["DISCIPLINA"]
    .astype(str)
    .str.upper()
    .str.strip()
)

mask_topicos = (
    graduacao_filtrada["DISCIPLINA_LIMPA"].str.contains("TÓPICOS|TOPICOS", na=False)
    &
    graduacao_filtrada["DISCIPLINA_LIMPA"].str.contains("MATEM", na=False)
)

# Remove apenas Tópicos Essenciais de Matemática quando nota = 0
graduacao_media = graduacao_filtrada[
    ~((mask_topicos) & (graduacao_filtrada["NOTA FINAL"] == 0))
].copy()

# =========================
# MÉDIA POR ALUNO
# =========================

medias_alunos = (
    graduacao_media
    .groupby(["Aluno", "CURSO", "Insper One"], as_index=False)["NOTA FINAL"]
    .mean()
    .rename(columns={"NOTA FINAL": "Média Graduação"})
)

st.subheader("Média por aluno")
st.dataframe(
    medias_alunos,
    use_container_width=True
)

# =========================
# COMPARAÇÃO INSPER ONE VS NÃO
# =========================

comparacao_insper_one = (
    medias_alunos
    .groupby("Insper One", as_index=False)["Média Graduação"]
    .mean()
    .rename(columns={"Média Graduação": "Média Geral dos Alunos"})
)

st.subheader("Comparação: Insper One vs. Não Insper One")

st.dataframe(
    comparacao_insper_one,
    use_container_width=True
)

fig_bar = px.bar(
    comparacao_insper_one,
    x="Insper One",
    y="Média Geral dos Alunos",
    color="Insper One",
    text="Média Geral dos Alunos",
    color_discrete_map={
        "Sim": "#1ABC9C",   # verde
        "Não": "#E6002D"    # vermelho
    },
    title="Média da graduação: Insper One vs. Não Insper One",
    labels={
        "Insper One": "Insper One",
        "Média Geral dos Alunos": "Média geral"
    }
)

fig_bar.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig_bar.update_layout(
    template="plotly_white",
    yaxis_range=[0, 10],
    showlegend=False,
    xaxis_title="Insper One",
    yaxis_title="Média geral"
)

st.plotly_chart(fig_bar, use_container_width=True)

# =========================
# HISTOGRAMA DAS MÉDIAS DOS ALUNOS
# =========================

st.subheader("Distribuição das médias dos alunos")

media_geral = medias_alunos["Média Graduação"].mean()
desvio_padrao = medias_alunos["Média Graduação"].std()

cores_insper_one = {
    "Sim": "#1ABC9C",
    "Não": "#E6002D",
    "Todos": "#636EFA"
}

medias_sim = medias_alunos[medias_alunos["Insper One"] == "Sim"].copy()
medias_nao = medias_alunos[medias_alunos["Insper One"] == "Não"].copy()

media_geral = medias_alunos["Média Graduação"].mean()
dp_geral = medias_alunos["Média Graduação"].std()

media_sim = medias_sim["Média Graduação"].mean()
dp_sim = medias_sim["Média Graduação"].std()

media_nao = medias_nao["Média Graduação"].mean()
dp_nao = medias_nao["Média Graduação"].std()


col_h1, col_h2, col_h3 = st.columns(3)

with col_h1:
    st.metric("Média geral", round(media_geral, 2))
    st.metric("Desvio padrão geral", round(dp_geral, 2))

with col_h2:
    st.metric("Média Insper One", round(media_sim, 2))
    st.metric("Desvio padrão Insper One", round(dp_sim, 2))

with col_h3:
    st.metric("Média sem Insper One", round(media_nao, 2))
    st.metric("Desvio padrão sem Insper One", round(dp_nao, 2))
col_hist1, col_hist2 = st.columns(2)

with col_hist1:
    fig_sim = px.histogram(
        medias_sim,
        x="Média Graduação",
        nbins=10,
        histnorm="probability density",
        title="Alunos Insper One",
        labels={
            "Média Graduação": "Média da graduação",
            "probability density": "Densidade"
        },
        color_discrete_sequence=[cores_insper_one["Sim"]]
    )

    fig_sim.add_vline(
        x=media_sim,
        line_dash="dash",
        line_color="black",
        annotation_text=f"Média = {media_sim:.2f}",
        annotation_position="top right"
    )



    fig_sim.update_layout(
        template="plotly_white",
        xaxis_title="Média da graduação",
        yaxis_title="Densidade",
        bargap=0.05,
        showlegend=False
    )

    st.plotly_chart(fig_sim, use_container_width=True)

with col_hist2:
    fig_nao = px.histogram(
        medias_nao,
        x="Média Graduação",
        nbins=10,
        histnorm="probability density",
        title="Alunos sem Insper One",
        labels={
            "Média Graduação": "Média da graduação",
            "probability density": "Densidade"
        },
        color_discrete_sequence=[cores_insper_one["Não"]]
    )

    fig_nao.add_vline(
        x=media_nao,
        line_dash="dash",
        line_color="black",
        annotation_text=f"Média = {media_nao:.2f}",
        annotation_position="top right"
    )




    fig_nao.update_layout(
        template="plotly_white",
        xaxis_title="Média da graduação",
        yaxis_title="Densidade",
        bargap=0.05,
        showlegend=False
    )

    st.plotly_chart(fig_nao, use_container_width=True)

st.subheader("Distribuição geral das médias")

fig_geral = px.histogram(
    medias_alunos,
    x="Média Graduação",
    nbins=10,
    histnorm="probability density",
    title="Todos os alunos",
    labels={
        "Média Graduação": "Média da graduação",
        "probability density": "Densidade"
    },
    color_discrete_sequence=[cores_insper_one["Todos"]]
)

fig_geral.add_vline(
    x=media_geral,
    line_dash="dash",
    line_color="black",
    annotation_text=f"Média = {media_geral:.2f}",
    annotation_position="top right"
)


fig_geral.update_layout(
    template="plotly_white",
    xaxis_title="Média da graduação",
    yaxis_title="Densidade",
    bargap=0.05,
    showlegend=False
)

st.plotly_chart(fig_geral, use_container_width=True)

# =========================
# TESTE T DE DIFERENÇA DE MÉDIAS - WELCH
# =========================

st.divider()
st.subheader("Teste t de diferença de médias")

grupo_sim = medias_alunos.loc[
    medias_alunos["Insper One"] == "Sim",
    "Média Graduação"
].dropna()

grupo_nao = medias_alunos.loc[
    medias_alunos["Insper One"] == "Não",
    "Média Graduação"
].dropna()

if len(grupo_sim) < 2 or len(grupo_nao) < 2:
    st.warning("Não há observações suficientes nos dois grupos para realizar o teste.")
else:
    media_sim = grupo_sim.mean()
    media_nao = grupo_nao.mean()

    var_sim = grupo_sim.var(ddof=1)
    var_nao = grupo_nao.var(ddof=1)

    n_sim = len(grupo_sim)
    n_nao = len(grupo_nao)

    diferenca = media_sim - media_nao

    # Erro-padrão robusto a variâncias diferentes
    erro_padrao = ((var_sim / n_sim) + (var_nao / n_nao)) ** 0.5

    t_stat = diferenca / erro_padrao

    # Graus de liberdade de Welch-Satterthwaite
    gl_welch = (
        (var_sim / n_sim + var_nao / n_nao) ** 2
        /
        (
            ((var_sim / n_sim) ** 2) / (n_sim - 1)
            +
            ((var_nao / n_nao) ** 2) / (n_nao - 1)
        )
    )

    # Teste unilateral: H1: média IONE > média sem IONE
    p_valor = stats.t.sf(t_stat, df=gl_welch)

    resultado_teste = pd.DataFrame({
        "Estatística": [
            "Média Insper One",
            "Média sem Insper One",
            "Diferença de médias",
            "Variância Insper One",
            "Variância sem Insper One",
            "Erro-padrão",
            "Estatística t",
            "p-valor unilateral",
            "N Insper One",
            "N sem Insper One"
        ],
        "Valor": [
            media_sim,
            media_nao,
            diferenca,
            var_sim,
            var_nao,
            erro_padrao,
            t_stat,
            p_valor,
            n_sim,
            n_nao
        ]
    })

    st.markdown(
        """
        **Hipóteses do teste**

        H₀: média dos alunos Insper One − média dos alunos sem Insper One = 0

        H₁: média dos alunos Insper One − média dos alunos sem Insper One > 0
        """
    )

    st.dataframe(
        resultado_teste.round(4),
        use_container_width=True,hide_index=True
    )

    alpha = 0.05

    if p_valor < alpha:
        st.success(
            f"Como o p-valor unilateral é {p_valor:.4f}, rejeitamos H₀ ao nível de 5%. "
            "Há evidência estatística de que a média dos alunos Insper One é maior."
        )
    else:
        st.info(
            f"Como o p-valor unilateral é {p_valor:.4f}, não rejeitamos H₀ ao nível de 5%. "
            "Não há evidência estatística suficiente de que a média dos alunos Insper One seja maior."
        )
