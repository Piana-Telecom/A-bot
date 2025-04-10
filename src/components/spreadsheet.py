import pandas as pd
import streamlit as st
import xlsxwriter  # type: ignore
from io import BytesIO


def generate_spreadsheet(df: pd.DataFrame):
    # Filtra apenas etapas relevantes
    etapas_validas = ["DADOS DE PROJETO", "CONFERENCIA", "RESULTADO"]
    df = df[df["DS_Etapa"].isin(etapas_validas)]

    # Agrupa por DS_Servico e DS_Etapa, somando QuantidadeAplicada
    df_grouped = (
        df.groupby(["DS_Servico", "DS_Etapa"])["QuantidadeAplicada"]
        .sum()
        .unstack(fill_value=0)
    )

    # Renomeia as colunas
    df_grouped = df_grouped.rename(
        columns={
            "DADOS DE PROJETO": "ENTRADA",
            "CONFERENCIA": "CONFERÊNCIA",
            "RESULTADO": "PROTOCOLO",
        }
    )

    # Remove serviços que não possuem as 3 colunas
    df_grouped = df_grouped[
        (df_grouped["ENTRADA"] != 0)
        & (df_grouped["CONFERÊNCIA"] != 0)
        & (df_grouped["PROTOCOLO"] != 0)
    ]

    # Calcula a diferença
    df_grouped["DIFERENÇA"] = (df_grouped["ENTRADA"] - df_grouped["PROTOCOLO"]).round(3)

    # Ajusta o índice como coluna
    df_grouped = df_grouped.reset_index()
    df_grouped = df_grouped[
        ["DS_Servico", "ENTRADA", "CONFERÊNCIA", "PROTOCOLO", "DIFERENÇA"]
    ]
    df_grouped = df_grouped.rename(columns={"DS_Servico": "PROJETO"})

    # Criar planilha com formatação
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("Resumo")

    # Estilos
    header_format = workbook.add_format(
        {
            "bold": True,
            "bg_color": "#305496",
            "font_color": "white",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
        }
    )

    cell_format = workbook.add_format(
        {"border": 1, "align": "center", "valign": "vcenter"}
    )

    number_format = workbook.add_format(
        {"border": 1, "num_format": "0.000", "align": "center", "valign": "vcenter"}
    )

    # Ajuste de largura das colunas
    worksheet.set_column("A:A", 80)
    worksheet.set_column("B:E", 15)

    # Cabeçalhos
    colunas = ["PROJETO", "ENTRADA", "CONFERÊNCIA", "PROTOCOLO", "DIFERENÇA"]
    for col_num, col_name in enumerate(colunas):
        worksheet.write(0, col_num, col_name, header_format)

    # Dados
    for row_num, row in enumerate(df_grouped.itertuples(index=False), start=1):
        worksheet.write(row_num, 0, row[0], cell_format)
        worksheet.write_number(row_num, 1, row[1], number_format)
        worksheet.write_number(row_num, 2, row[2], number_format)
        worksheet.write_number(row_num, 3, row[3], number_format)
        worksheet.write_number(row_num, 4, row[4], number_format)

    workbook.close()
    output.seek(0)

    # Botão de download
    st.download_button(
        label="📥 Baixar planilha Excel",
        data=output,
        file_name="planilha_resultado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
