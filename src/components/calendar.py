import streamlit as st
import pandas as pd
from datetime import date, timedelta


def filtrar_por_data(df: pd.DataFrame) -> pd.DataFrame:
    today = date.today() - timedelta(days=30)
    thirty_days_ago = today - timedelta(days=60)

    # Converte colunas para datetime.date
    df["DT_Atividade"] = pd.to_datetime(df["DT_Atividade"], errors="coerce").dt.date
    df["DT_Conclusao"] = pd.to_datetime(df["DT_Conclusao"], errors="coerce").dt.date

    # Remove linhas com datas inválidas
    df = df.dropna(subset=["DT_Atividade", "DT_Conclusao"])

    # Define intervalo disponível
    min_date = min(df["DT_Atividade"].min(), df["DT_Conclusao"].min())
    max_date = max(df["DT_Atividade"].max(), df["DT_Conclusao"].max())

    # Inputs para o usuário
    st.write("### Filtrar por janela de tempo")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Data inicial",
            min_value=min_date,
            max_value=max_date,
            value=thirty_days_ago,
            format="DD/MM/YYYY",
        )
    with col2:
        end_date = st.date_input(
            "Data final",
            min_value=min_date,
            max_value=max_date,
            value=today,
            format="DD/MM/YYYY",
        )

    # Aplica o filtro
    df_filtrado = df[
        ((df["DT_Atividade"] >= start_date) & (df["DT_Atividade"] <= end_date))
        | ((df["DT_Conclusao"] >= start_date) & (df["DT_Conclusao"] <= end_date))
    ]

    # Formata as datas para string brasileira
    df_filtrado["DT_Atividade"] = pd.to_datetime(
        df_filtrado["DT_Atividade"]
    ).dt.strftime("%d-%m-%Y")
    df_filtrado["DT_Conclusao"] = pd.to_datetime(
        df_filtrado["DT_Conclusao"]
    ).dt.strftime("%d-%m-%Y")

    return df_filtrado
