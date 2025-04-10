import streamlit as st
from backend.db import get_filtered_data
from components.calendar import filtrar_por_data
from components.spreadsheet import generate_spreadsheet


st.set_page_config(page_title="A-bot", layout="wide")
st.title("A-Bot : Automação Aliance")

df = get_filtered_data()
df_filtrado = filtrar_por_data(df)

generate_spreadsheet(df_filtrado)
st.write("### Resultado filtrado")
st.dataframe(df_filtrado)
