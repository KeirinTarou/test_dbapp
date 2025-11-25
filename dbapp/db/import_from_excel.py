import os
import time
import pandas as pd
import win32com.client
import pythoncom
from dotenv import load_dotenv
from datetime import datetime

# `.env`読み込み
load_dotenv()

from dbapp.db.connection import CONNECTION_STRING

EXCEL_PATH = os.path.join(os.path.dirname(__file__), "source.xlsm")
STATUS_SHEET = "Status"
DATA_SHEET = "Data"
STATUS_CELL = "A1"
ERROR_CELL = "A2"
STATUS_DONE = "Done!!"
STATUS_ERROR = "Error..."
STATUS_WORKING = "Working..."

def normalize_value(v):
    """ 値を正規化する
    """
    # NoneはNULLに補正
    if v is None:
        return 'NULL'
    # 整数値を補正
    elif isinstance(v, float) and v.is_integer():
        return int(v)
    elif isinstance(v, datetime):
        return v.strftime('%Y-%m-%d %H:%M:%S')
    return v

def fetch_all_excel(query: str, params=None, timeout: int=30):
    """ Excel経由でDBからレコードセットを取得
        (columns, rows)の形で結果を返却
    """
    # プレースホルダがあるときはパラメータを埋め込む
    if params is None:
        params = ()
    else:
        # `params`をアンパックして`?`の部分に順番に埋め込む
        # `params`が`("foo", "bar", 2000)`だったら、
        # `"{} {} {}".format(*["foo", "bar", 2000])`となり、
        # `"{} {} {}".format("foo", "bar", 2000)`と同義となる
        # 結果、`query`に3つあるはずの`?`に、
        # 順に"foo", "bar", 2000が埋め込まれる
        query = query.replace("?", "{}").format(*[
            f"'{p}'" if isinstance(p, str) else p for p in params
        ])

    # Flaskのスレッド内でCOMを初期化
    pythoncom.CoInitialize()

    try:
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        wb = excel.Workbooks.Open(EXCEL_PATH)

        try:
            return _execute_query_on_excel(excel=excel, wb=wb, query=query, timeout=timeout)
        finally:
            wb.Close(SaveChanges=False)
            excel.Quit()
    
    finally:
        # あとかたづけ
        pythoncom.CoUninitialize()

from dbapp.db.exceptions import (
    DatabaseExecutionError, 
    QuerySyntaxError, 
    QueryRuntimeError
)
def fetch_both_with_single_excel(user_query, answer_query, timeout=30):
    print("fetch_both_with_single_excel() executed!!")
    role_user = "ユーザ投稿クエリ"
    role_answer = "正解クエリ"
    pythoncom.CoInitialize()
    try: 
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        wb = excel.Workbooks.Open(EXCEL_PATH)

        try:
            try:
                # ユーザクエリの結果セット取得
                user_cols, user_rows = _execute_query_on_excel(excel, wb, user_query, timeout)
            except Exception:
                _raise_excel_db_error(role=role_user, wb=wb)
            try:
                # 正解クエリの結果セット取得
                answer_cols, answer_rows = _execute_query_on_excel(excel, wb, answer_query, timeout)
            except Exception:
                _raise_excel_db_error(role=role_answer, wb=wb)
            
            return user_cols, user_rows, answer_cols, answer_rows 
        finally: 
            wb.Close(SaveChanges=False)
            excel.Quit()
    finally:
        pythoncom.CoUninitialize()

def _execute_query_on_excel(excel, wb, query, timeout):
    # 踏み台Excelブックのマクロに引数を渡して実行
    excel.Run(
        "Std01Main.RefreshFromDB", 
        CONNECTION_STRING.replace("\n", ""), 
        query, 
        timeout
    )

    # 完了待ち
    while True:
        status = wb.Sheets(STATUS_SHEET).Range(STATUS_CELL).Value 
        if status == STATUS_DONE:
            break
        elif status == STATUS_ERROR:
            err_msg = wb.Sheets(STATUS_SHEET).Range(ERROR_CELL).Value
            raise RuntimeError(err_msg)
        time.sleep(0.5)

    # 結果取得
    ws = wb.Sheets(DATA_SHEET)
    data = ws.UsedRange.Value
    # data[0] -> カラム名の行
    # data[1:] -> データの行

    if not data or len(data) < 2:
        # データがない
        return [], []

    # カラム名のリスト
    columns = list(data[0])
    # データ行のリスト（タプルのリスト）
    rows = [tuple(normalize_value(x) for x in r) for r in data[1:]]

    # 結果を返却
    return columns, rows

def _raise_excel_db_error(role: str, wb):
    status = wb.sheets("Status").Range("A1").Value
    err_desc = wb.sheets("Status").Range("A2").Value
    if status == "Error...":
        if "syntax" in err_desc.lower():
            raise RuntimeError(f"{role}（SQL構文エラー）: {err_desc}")
        elif "timeout" in err_desc.lower():
            raise RuntimeError(f"{role}（SQL実行時エラー）: {err_desc}")
        else:
            raise RuntimeError(f"{role}（DBエラー）: {err_desc}")
    else:
        # DBエラー以外のExcel起因の例外
        raise RuntimeError(f"{role}（Excel実行エラー）")

def describe_table(table_name: str):
    """ `DESC`コマンドを使ってテーブル構造を取得
    """
    query = f"DESC {table_name};"
    return fetch_all_excel(query)