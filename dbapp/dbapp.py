from flask import (
    Flask, render_template, abort, request, flash, redirect, 
    url_for, session)
from dotenv import load_dotenv
# import pyodbc

from dbapp.config import (
    DEFAULT_EDITOR_HEIGHT, 
    DEFAULT_COLUMNS, DEFAULT_ROWS, 
)

import dbapp.db.queries as dbq
import dbapp.db.import_from_excel as db_excel
import re
from datetime import datetime
import os
from dbapp.services.file_service import save_query_to_file
from dbapp.services.query_service import exec_query
from dbapp.services.session_service import (
    # エディタの高さ関連
    save_query_editor_height, load_query_editor_height, 
    # エディタへのスクロールフラグ
    set_scroll_to_editor, pop_scroll_to_editor, 
)

# `.env`読み込み
load_dotenv()

app = Flask(__name__)

# セッション用の秘密鍵設定
app.secret_key = "kps"

# クエリ保存用フォルダを用意
STORAGE_DIR = os.path.join(os.getcwd(), "storage", "queries")
os.makedirs(STORAGE_DIR, exist_ok=True)

def _exec_sql_query(sql_query, use_excel=False):
    # クエリ実行 -> レコードセット取得
    columns, rows, message, category = exec_query(sql_query)
    # フラッシュメッセージ
    flash(message, category)
    # セッションにスクロールフラグを立てる
    set_scroll_to_editor(True)
    # レコードセットを返す
    return columns, rows

# トップページ
@app.route("/", methods=["GET", "POST"])
def index():
    # ローカル変数初期化
    sql_query: str = ''
    columns: list = []
    rows: list = []
    scroll_to_editor: bool = False
    # POSTリクエストのとき
    if request.method == "POST":
        # フォームからクエリを取得
        sql_query = request.form.get("sql_query", "").strip()

        # CodeMirrorラッパーの高さを保存
        sql_query_height = request.form.get("sql_query_height")
        if sql_query_height:
            # エディタの高さをセッションに保存
            save_query_editor_height(
                sql_query_height=sql_query_height
            )
        
        # 「保存」ボタンが押された
        if "save" in request.form:
            # ユーザが入力したファイル名を取得
            user_filename = request.form.get("filename", "").strip()
            # クエリ保存関数呼び出し
            filename, message, category = save_query_to_file(
                sql_query=sql_query, 
                user_filename=user_filename, 
                storage_dir=STORAGE_DIR)

            flash(f"{message}{filename}", category)

            # エディタのクエリをセッションに保存
            session["last_posted_query"] = sql_query
            # セッションにスクロールフラグを立てる
            set_scroll_to_editor(True)
            # トップページにリダイレクト
            return redirect(url_for("index"))
        elif "execute" in request.form:
            # クエリ実行 -> レコードセット取得
            columns, rows = _exec_sql_query(sql_query, use_excel=False)

    # GETリクエストのとき
    else:
        # セッションに保存した直近のクエリをテンプレートに渡す
        sql_query = session.pop("last_posted_query", "")
        # デフォルトの擬似テーブルを表示
        columns, rows = [DEFAULT_COLUMNS, DEFAULT_ROWS]

    # エディタの高さ情報をセッションから取り出し
    sql_query_height = load_query_editor_height()
    # エディタへのスクロールフラグをセッションから取り出し
    scroll_to_editor = pop_scroll_to_editor()

    # レコードセットをテンプレートに渡す
    return render_template(
        "pages/index.html", 
        columns=columns, 
        rows=rows, 
        table_names=dbq.TABLE_NAMES, 
        sql_query=sql_query, 
        sql_query_height=sql_query_height, 
        scroll_to_editor=scroll_to_editor
    )

# 各テーブルの構造データ（JSON）を返すWeb API
@app.route("/api/table/<table_name>")
def api_table_structure(table_name):
    allowed_tables = dbq.TABLE_NAMES
    if table_name not in allowed_tables:
        # JSONとステータスコード（`400`: Bad Request）を返す
        return {"error": "Invalid table name"}, 400
    # `fields`: カラム名のリスト
    # `values`: `Row`オブジェクトのリスト
    fields, values = dbq.describe_table(table_name)
    # fields, values = db_excel.describe_table(table_name)
    # Rowオブジェクトをリストに変換してリストのリストにする
    rows_list = [list(row) for row in values]
    # クライアントにJSONを返す
    return {
        "columns": fields, 
        "rows": rows_list, 
    }

# クエリを実行するだけのページ
@app.route('/playground', methods=['GET', 'POST'])
def playground():
    # ローカル変数初期化
    sql_query: str = ''
    columns: list = []
    rows: list = []
    scroll_to_editor: bool = False

    if request.method == 'POST':
        sql_query = request.form.get('sql_query', '')
        # クエリ実行 -> レコードセット取得
        columns, rows = _exec_sql_query(sql_query, use_excel=False)
    else:
        # セッションに保存した直近のクエリをテンプレートに渡す
        sql_query = session.pop("last_posted_query", "")
        # デフォルトの擬似テーブルを表示
        columns, rows = [DEFAULT_COLUMNS, DEFAULT_ROWS]

    # エディタの高さ情報をセッションから取り出し
    sql_query_height = load_query_editor_height()
    # エディタへのスクロールフラグをセッションから取り出し
    scroll_to_editor = pop_scroll_to_editor()
    
    return render_template(
        'pages/playground.html', 
        columns=columns, 
        rows=rows, 
        table_names=dbq.TABLE_NAMES,
        sql_query=sql_query, 
        sql_query_height=sql_query_height, 
        scroll_to_editor=scroll_to_editor
    )

# 各テーブルの構造表示用ページ
@app.route("/table/<table_name>")
def show_table_structure(table_name):
    # 表示するテーブル名のリスト
    allowed_tables = dbq.TABLE_NAMES
    # テーブル名がリストになかったら404
    if table_name not in allowed_tables:
        abort(404)
    
    # DESC文実行
    fields, values = dbq.describe_table(table_name)
    # fields, values = db_excel.describe_table(table_name)

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
