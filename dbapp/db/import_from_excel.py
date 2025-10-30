import os
import time
import pandas as pd
import win32com.client

base_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(base_dir, "db_bridge.xlsm")

excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = False
wb = excel.Workbooks.Open(excel_path)

sql = "SELECT TOP 10 * FROM Employees ORDER BY HireDate DESC"
excel.Run("Module1.RefreshFromDB", sql)

# 完了待ち
while wb.Names("RefreshFlag").RefersToRange.Value != "Done":
    time.sleep(0.5)

# 結果取得
ws = wb.Sheets("Data")
data = ws.UsedRange.Value
df = pd.DataFrame(data[1:], columns=data[0])
print(df.head())

wb.Close(SaveChanges=False)
excel.Quit()
