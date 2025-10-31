import pyodbc
import os

CONNECTION_STRING = f"""
DRIVER={ os.getenv('DB_DRIVER') };
SERVER={ os.getenv('DB_SERVER') };
PORT={ os.getenv('DB_PORT') };
DATABASE={ os.getenv('DB_DATABASE') };
UID={ os.getenv('DB_USER') };
PWD={ os.getenv('DB_PASSWORD') };
OPTION=3;
"""

def get_connection():
    """`pyodbc.Connection`インスタンスを返す
    """
    return pyodbc.connect(CONNECTION_STRING)