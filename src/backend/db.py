import pyodbc  # type: ignore
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../..", ".env"))


def get_filtered_data():
    conn_str = (
        f"DRIVER={{{os.getenv('ODBC_DRIVER')}}};"
        f"SERVER={os.getenv('ODBC_SERVER')};"
        f"DATABASE={os.getenv('ODBC_DATABASE')};"
        f"UID={os.getenv('ODBC_UID')};"
        f"PWD={os.getenv('ODBC_PWD')};"
        f"TrustServerCertificate={os.getenv('ODBC_TRUSTCERT')};"
        f"Encrypt={os.getenv('ODBC_ENCRYPT')};"
    )
    conn = pyodbc.connect(conn_str)

    query = """
        SELECT * FROM VTB_OSE_ETAPA_X_ATIVIDADE_X_TECNICO_BI
        WHERE ID_Atividade = 1
    """
    df = pd.read_sql(query, conn)
    df = df[df["DS_Servico"].str.upper().str.startswith("P", na=False)]
    conn.close()
    return df
