import os
import time
import pandas as pd
import win32com.client
from dotenv import load_dotenv

# `.env`読み込み
load_dotenv()

from connection import CONNECTION_STRING

EXCEL_PATH = os.path.join(os.path.dirname(__file__), "source.xlsm")
STATUS_SHEET = "Status"
DATA_SHEET = "Data"
STATUS_CELL = "A1"
STATUS_DONE = "Done!!"
STATUS_ERROR = "Error..."
STATUS_WORKING = "Working..."

def fetch_all_excel(query: str):
    """ Excel経由でDBからレコードセットを取得
        (columns, rows)の形で結果を返却
    """
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    wb = excel.Workbooks.Open(EXCEL_PATH)

    try:
        # 踏み台Excelブックのマクロに引数を渡して実行
        excel.Run(
            "Std01Main.RefreshFromDB", 
            CONNECTION_STRING.replace("\n", ""), 
            query
        )

        # 完了待ち
        while True:
            status = wb.Sheets(STATUS_SHEET).Range(STATUS_CELL).Value 
            if status == STATUS_DONE:
                break
            elif status == STATUS_ERROR:
                raise RuntimeError("ExcelでのDB処理中にエラーが発生しました。")
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
        rows = [tuple(r) for r in data[1:]]

        # 結果を返却
        return columns, rows

    finally:
        wb.Close(SaveChanges=False)
        excel.Quit()
