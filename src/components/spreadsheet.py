import pandas as pd
import streamlit as st
import xlsxwriter  # type: ignore
from io import BytesIO
import re
from backend.db import get_data_by_servico


def expandir_servicos_sucessores(df):
    df_resultado = df.copy()

    for servico in df["DS_Servico"].unique():
        match = re.match(r"([A-Z]+\d+)([A-Z]?)(\d*)\s+(.*)", servico)
        if not match:
            continue

        base_id = match.group(1)
        letra = match.group(2) or "A"
        numero_sufixo = match.group(3)
        sufixo_texto = match.group(4).strip()

        letra_ordem = ord(letra) + 1  # começa da próxima letra

        # Percorre letras (P10B, P10C, ...)
        while letra_ordem <= ord("Z"):
            sufixo = chr(letra_ordem)
            proximo_servico = f"{base_id}{sufixo} {sufixo_texto}"
            df_sucessor = get_data_by_servico(proximo_servico)
            print(f"[DEBUG] Buscando: {proximo_servico} → {len(df_sucessor)} linhas")

            if df_sucessor.empty:
                break

            df_resultado = adicionar_sucessor(df_resultado, df_sucessor, servico)
            letra_ordem += 1

        # Percorre sufixos numéricos (P10A1, P10A2, ...)
        numero_ordem = 1
        while True:
            sufixo = f"{letra}{numero_ordem}"
            proximo_servico = f"{base_id}{sufixo} {sufixo_texto}"
            df_sucessor = get_data_by_servico(proximo_servico)
            print(f"[DEBUG] Buscando: {proximo_servico} → {len(df_sucessor)} linhas")

            if df_sucessor.empty:
                break

            df_resultado = adicionar_sucessor(df_resultado, df_sucessor, servico)
            numero_ordem += 1

    return df_resultado


def adicionar_sucessor(df_resultado, df_sucessor, servico_original):
    # Separa os dados por tipo
    conferencia_df = df_sucessor[df_sucessor["DS_Etapa"].str.upper() == "CONFERENCIA"][
        ["DS_Servico", "DS_Etapa", "QuantidadeAplicada"]
    ].copy()

    protocolo_df = df_sucessor[
        df_sucessor["DS_Etapa"].str.upper().str.startswith("PROTOCOLO")
    ][["DS_Servico", "DS_Etapa", "DS_Atividade"]].copy()

    # Renomeia colunas para unificar no final
    conferencia_df["Valor"] = conferencia_df["QuantidadeAplicada"]
    protocolo_df["Valor"] = pd.to_numeric(protocolo_df["DS_Atividade"], errors="coerce")

    # Normaliza nome da etapa protocolo
    protocolo_df["DS_Etapa"] = "DADOS PROTOCOLO"

    # Junta os dois
    df_extra = pd.concat(
        [
            conferencia_df[["DS_Servico", "DS_Etapa", "Valor"]],
            protocolo_df[["DS_Servico", "DS_Etapa", "Valor"]],
        ]
    )

    # Substitui DS_Servico pelo original (o A, que está no df principal)
    df_extra["DS_Servico"] = servico_original

    # Adiciona ao dataframe original, com mesma estrutura
    df_extra = df_extra.rename(columns={"Valor": "QuantidadeAplicada"})
    return pd.concat([df_resultado, df_extra], ignore_index=True)


def generate_spreadsheet(df: pd.DataFrame):
    df = expandir_servicos_sucessores(df)
    # Considera todas as etapas relevantes
    etapas_validas = ["DADOS DE PROJETO", "CONFERENCIA", "RESULTADO", "DADOS PROTOCOLO"]
    df = df[df["DS_Etapa"].isin(etapas_validas)]

    # Substitui nomes para facilitar
    df["DS_Etapa"] = df["DS_Etapa"].replace(
        {"DADOS DE PROJETO": "ENTRADA", "CONFERENCIA": "CONFERÊNCIA"}
    )

    # Cria cópias dos protocolos
    # Verifica quais serviços têm DADOS PROTOCOLO
    servicos_com_dados_protocolo = set(
        df[df["DS_Etapa"] == "DADOS PROTOCOLO"]["DS_Servico"]
    )

    # Cria cópias dos protocolos
    df_resultado = df[
        (df["DS_Etapa"] == "RESULTADO")
        & (~df["DS_Servico"].isin(servicos_com_dados_protocolo))
    ].copy()
    df_resultado["DS_Etapa"] = "PROTOCOLO"

    df_dados_protocolo = df[df["DS_Etapa"] == "DADOS PROTOCOLO"].copy()
    df_dados_protocolo["DS_Etapa"] = "PROTOCOLO"

    # Agrupa todos os dados
    df_protocolo_final = pd.concat([df, df_resultado, df_dados_protocolo])

    # Agora agrupa tudo
    df_grouped = (
        df_protocolo_final.groupby(["DS_Servico", "DS_Etapa"])["QuantidadeAplicada"]
        .sum()
        .unstack(fill_value=0)
    )

    # Garante colunas
    for col in ["ENTRADA", "CONFERÊNCIA", "PROTOCOLO"]:
        if col not in df_grouped.columns:
            df_grouped[col] = 0

    # Seleciona apenas os projetos com ENTRADA e CONFERÊNCIA
    df_grouped = df_grouped[
        (df_grouped["ENTRADA"] != 0) & (df_grouped["CONFERÊNCIA"] != 0)
    ]

    # Calcula diferença
    df_grouped["DIFERENÇA"] = (df_grouped["ENTRADA"] - df_grouped["PROTOCOLO"]).round(3)

    # Prepara o DataFrame final
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
    # Dados
    for row_num, row in enumerate(df_grouped.itertuples(index=False), start=1):
        worksheet.write(row_num, 0, row[0], cell_format)
        worksheet.write_number(row_num, 1, row[1], number_format)
        worksheet.write_number(row_num, 2, row[2], number_format)
        worksheet.write_number(row_num, 3, row[3], number_format)

        # Formatação condicional para diferença discrepante
        if abs(row[4]) > 2:  # valor de corte, pode ajustar
            red_format = workbook.add_format(
                {
                    "bg_color": "#C00000",
                    "font_color": "white",
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "num_format": "0.000",
                }
            )
            worksheet.write_number(row_num, 4, row[4], red_format)
        else:
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
