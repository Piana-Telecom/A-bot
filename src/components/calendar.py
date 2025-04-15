import streamlit as st
import pandas as pd
from datetime import date


def filtrar_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    # Converte as colunas de data
    df["DT_Atividade"] = pd.to_datetime(df["DT_Atividade"], errors="coerce")
    df["DT_Conclusao"] = pd.to_datetime(df["DT_Conclusao"], errors="coerce")

    # Remove linhas com datas inválidas
    df = df.dropna(subset=["DT_Atividade"])

    # Criar colunas auxiliares de mês e ano
    df["ano"] = df["DT_Atividade"].dt.year
    df["mes"] = df["DT_Atividade"].dt.month

    # Opções para seleção
    anos_disponiveis = sorted(df["ano"].unique())
    meses_disponiveis = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro",
    }

    st.write("### Filtrar por mês de início da etapa 'DADOS DE PROJETO'")
    col1, col2 = st.columns(2)
    with col1:
        ano = st.selectbox("Ano", anos_disponiveis, index=len(anos_disponiveis) - 1)
    with col2:
        mes = st.selectbox(
            "Mês",
            list(meses_disponiveis.keys()),
            format_func=lambda x: meses_disponiveis[x],
        )

    # Identifica os serviços que começaram a etapa "DADOS DE PROJETO" no mês/ano selecionado
    servicos_filtrados = df[
        (df["DS_Etapa"].str.upper() == "DADOS DE PROJETO")
        & (df["ano"] == ano)
        & (df["mes"] == mes)
    ]["DS_Servico"].unique()

    # Filtra todas as linhas relacionadas a esses serviços
    df_resultado = df[df["DS_Servico"].isin(servicos_filtrados)].copy()

    if df_resultado.empty:
        st.warning("Nenhuma atividade encontrada para o mês selecionado.")
        return pd.DataFrame()

    # Formata datas para exibição
    df_resultado["DT_Atividade"] = df_resultado["DT_Atividade"].dt.strftime("%d-%m-%Y")
    df_resultado["DT_Conclusao"] = df_resultado["DT_Conclusao"].dt.strftime("%d-%m-%Y")

    # Remove colunas auxiliares
    df_resultado = df_resultado.drop(columns=["ano", "mes"])

    return df_resultado
