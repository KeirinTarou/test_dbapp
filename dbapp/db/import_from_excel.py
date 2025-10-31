import os
import time
import pandas as pd
import win32com.client
from dotenv import load_dotenv

# `.env`読み込み
load_dotenv()

from connection import CONNECTION_STRING

base_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(base_dir, "source.xlsm")

excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = False
wb = excel.Workbooks.Open(excel_path)

sql = "SELECT * FROM CustomerClasses;"
excel.Run("Std01Main.RefreshFromDB", CONNECTION_STRING.replace("\n", ""), sql)

# 完了待ち
while wb.Sheets("Status").Range("A1").Value != "Done!!":
    time.sleep(0.5)

# 結果取得
ws = wb.Sheets("Data")
data = ws.UsedRange.Value
df = pd.DataFrame(data[1:], columns=data[0])
print(df.head())

wb.Close(SaveChanges=False)
excel.Quit()
