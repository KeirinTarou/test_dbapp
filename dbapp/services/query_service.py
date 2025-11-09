from dbapp.db import queries as dbq
from dbapp.db.import_from_excel import fetch_all_excel

# クエリ実行失敗時返却用データ（笑）
FAILED_COLUMNS = ["( ´,_ゝ`)", "ち～ん（笑）"]
FAILED_ROWS = [
    ["残念ｗ", "レコードセットが返らなかったよｗｗｗ"]
]

def exec_query(sql_query, use_excel=False):
    """ SQLクエリを安全に実行し、
        (columns, rows, message, category)を返す
    """
    try:
        # 構文チェック & 無害化
        safe_query = dbq.sanitize_and_validate_sql(
            sql_query=sql_query, 
            allowed_start=("SELECT", "WITH")
        )
        
        # データ取得
        # Excelを踏み台にする
        if use_excel:
            columns, rows = fetch_all_excel(safe_query)
        # 通常のDB接続
        else:
            columns, rows = dbq.fetch_all(safe_query)
        
        # 成功メッセージ
        return columns, rows, "クエリは正常に実行されました。", "success"
    except ValueError as e:
        return [], [], f"( ´,_ゝ｀) < {e}", "error"
    except Exception as e:
        columns, rows = FAILED_COLUMNS, FAILED_ROWS.copy()
        rows.append(["原因はたぶん……", str(e)[:200] + "..."])
        return columns, rows, "( ´,_ゝ`) < クエリ実行に失敗しました。", "error"
