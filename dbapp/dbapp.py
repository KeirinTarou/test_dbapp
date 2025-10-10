from flask import Flask, render_template, abort
import pyodbc
import db.queries as db

app = Flask(__name__)

# トップページ
@app.route("/")
def index():
    # DBに接続してレコードセットを取得
    columns, rows = db.fetch_all(db.TEST_QUERY)

    # レコードセットをテンプレートに渡す
    return render_template(
        "pages/index.html", 
        columns=columns, 
        rows=rows, 
        table_names=db.TABLE_NAMES
    )

# 各テーブルの構造表示用ページ
@app.route("/table/<table_name>")
def show_table_structure(table_name):
    # 表示するテーブル名のリスト
    allowed_tables = db.TABLE_NAMES
    # テーブル名がリストになかったら404
    if table_name not in allowed_tables:
        abort(404)
    
    # DESC文実行
    fields, values = db.describe_table(table_name)

    # テンプレートにデータを投げる
    return render_template(
        "pages/table.html", 
        table_names=allowed_tables, 
        table_name=table_name, 
        columns=fields, 
        rows=values
    )

if __name__ == "__main__":
    app.run(debug=True)
