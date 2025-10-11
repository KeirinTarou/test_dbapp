from db.connection import get_connection
import re

TEST_QUERY = """
SELECT
    *
FROM
    Employees
ORDER BY
    EmployeeID ASC
LIMIT 
    5
;
"""

TEST_QUERY_2 = """
DESC Employees;
"""

TABLE_NAMES = [
    "BelongTo", "Categories", "CustomerClasses", "Customers", 
    "Departments", "Employees", "Prefecturals", "Products", 
    "Salary", "Sales"
]

def fetch_all(query: str):
    """クエリを渡して全件取得する
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            # カラム名のリストを取得
            columns = [col[0] for col in cur.description]
            # レコードセットを取得（`pydoc.Row`オブジェクトのリスト）
            rows = cur.fetchall()
            # カラム名のリストと`Row`オブジェクトのリストを返却
            return columns, rows

def describe_table(table_name: str):
    """`DESC`コマンドを使ってテーブル構造を取得
    """
    query = f"DESC {table_name};"
    return fetch_all(query)

def sanitize_sql(sql_query: str) -> str:
    """SQL文からコメントや不要な空白を除去する
    """
    # ブロックコメント削除
    sql = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)
    # 行コメント削除
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    # 前後の空白除去
    return sql.strip()

def valid_sql(sql_query: str, allowed_start=("SELECT", )) -> bool:
    """SQL文が安全かどうかを判定する
        先頭キーワードが`allowed_start`のいずれかであることをチェック
        コメントや空白は無視して判定
    """
    clean_sql = sanitize_sql(sql_query)
    if not clean_sql:
        return False
    for kw in allowed_start:
        if clean_sql.upper().startswith(kw):
            return True
    # ここにたどり着いたということは`allowed_start`で始まらないということ
    return False
