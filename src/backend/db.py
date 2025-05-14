import pandas as pd
from sqlalchemy import create_engine  # type: ignore
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../..", ".env"))


def get_engine():
    # Monta string de conexão no formato que o SQLAlchemy espera
    conn_str = (
        f"mssql+pyodbc://{os.getenv('ODBC_UID')}:{os.getenv('ODBC_PWD')}"
        f"@{os.getenv('ODBC_SERVER')}/{os.getenv('ODBC_DATABASE')}"
        f"?driver={os.getenv('ODBC_DRIVER').replace(' ', '+')}"
        f"&TrustServerCertificate={os.getenv('ODBC_TRUSTCERT')}"
        f"&Encrypt={os.getenv('ODBC_ENCRYPT')}"
    )
    return create_engine(conn_str)


def get_filtered_data():
    engine = get_engine()
    query = """
        SELECT * FROM VTB_OSE_ETAPA_X_ATIVIDADE_X_TECNICO_BI
        WHERE ID_Atividade = 1
    """
    df = pd.read_sql(query, engine)
    df = df[df["DS_Servico"].str.upper().str.startswith("P", na=False)]
    return df


def get_data_by_servico(ds_servico: str):
    engine = get_engine()
    query = f"""
        SELECT * FROM VTB_OSE_ETAPA_X_ATIVIDADE_X_TECNICO_BI
        WHERE DS_Servico = '{ds_servico}'
        AND ID_Atividade IN (1, 2)
    """
    df = pd.read_sql(query, engine)
    return df
