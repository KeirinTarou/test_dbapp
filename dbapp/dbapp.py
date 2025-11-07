from flask import (
    Flask, render_template, abort, request, flash, redirect, 
    url_for, session)
from dotenv import load_dotenv
# import pyodbc
import db.queries as db
import db.import_from_excel as db_excel
import re
from datetime import datetime
import os

# `.env`読み込み
load_dotenv()

app = Flask(__name__)

# セッション用の秘密鍵設定
app.secret_key = "kps"

# クエリ保存用フォルダを用意
STORAGE_DIR = os.path.join(os.getcwd(), "storage", "queries")
os.makedirs(STORAGE_DIR, exist_ok=True)

# クエリ実行失敗時返却用データ（笑）
FAILED_COLUMNS = ["( ´,_ゝ`)", "ち～ん（笑）"]
FAILED_ROWS = [
    ["残念ｗ", "レコードセットが返らなかったよｗｗｗ"]
]

DEFAULT_COLUMNS = ["( ´_ゝ`)", "クエリ未実行"]
DEFAULT_ROWS = [
    ["(･ω･)", "クエリを入力して実行ボタンをクリックしてね！"]
]

DEFAULT_EDITOR_HEIGHT = 400

# トップページ
@app.route("/", methods=["GET", "POST"])
def index():
    # POSTリクエストのとき
    if request.method == "POST":
        # フォームからクエリを取得
        sql_query = request.form.get("sql_query", "").strip()

        # CodeMirrorラッパーの高さを保存
        sql_query_height = request.form.get("sql_query_height")
        if sql_query_height:
            try:
                session["sql_query_height"] = float(sql_query_height)
                # 値がおかしかったらデフォルト値をセット
            except ValueError:
                session["sql_query_height"] = DEFAULT_EDITOR_HEIGHT
        
        # 「保存」ボタンが押された
        if "save" in request.form:
            if not sql_query:
                flash("( ´,_ゝ｀) < クエリが空のため、保存できません。", "error")
            else:
                # ユーザが入力したファイル名を取得
                user_filename = request.form.get("filename", "").strip()

                if user_filename:
                    # 不正文字（/ \ : * ? " < > |）を`_`に置換
                    safe_name = re.sub(r'[\/\\:\*\?"<>\|]', '_', user_filename)
                else: 
                    # 未入力の場合はタイムスタンプをファイル名にする
                    safe_name = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
                # 拡張子を追加
                filename = f"{safe_name}.sql"

                # 保存先パスを取得
                path = os.path.join(STORAGE_DIR, filename)
                # ファイルに書き込み
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    # 書き込み時にCRLFをLFに置換
                    f.write(sql_query.replace("\r\n", "\n"))
                # フラッシュメッセージをセッションに保存
                flash(f"クエリを`.sql`ファイルとして保存しました。: {filename}", "success")

            # エディタのクエリをセッションに保存
            session["last_posted_query"] = sql_query
            # セッションにスクロールフラグを立てる
            session["scroll_to_editor"] = True
            # トップページにリダイレクト
            return redirect(url_for("index"))
        elif "execute" in request.form:
            # クエリ実行 -> レコードセット取得
            try:
                safe_query = db.sanitize_and_validate_sql(sql_query)
                # columns, rows = db.fetch_all(safe_query)
                columns, rows = db_excel.fetch_all_excel(safe_query)
                # クエリ実行成功のフラッシュメッセージ
                flash("クエリは正常に実行されました。", "success")
            # `ValueError`例外をキャッチ
            except ValueError as e:
                # 例外発生時のフラッシュメッセージ
                flash("( ´,_ゝ｀) < " + str(e), "error")
                columns, rows = [], []
            except Exception as e:
                # 例外発生時のフラッシュメッセージ
                flash("( ´,_ゝ`) < クエリ実行に失敗しました。", "error")
                columns = FAILED_COLUMNS
                rows = FAILED_ROWS.copy()
                # エラー情報を追加
                rows.append(["原因はたぶん……", str(e)[:200] + "..."])

            # セッションにスクロールフラグを立てる
            session["scroll_to_editor"] = True

    # GETリクエストのとき
    else:
        # セッションに保存した直近のクエリをテンプレートに渡す
        sql_query = session.pop("last_posted_query", "")
        # デフォルトの擬似テーブルを表示
        columns, rows = [DEFAULT_COLUMNS, DEFAULT_ROWS]

    # エディタの高さ情報をセッションから取り出し
    sql_query_height = session.get("sql_query_height", DEFAULT_EDITOR_HEIGHT)
    # エディタへのスクロールフラグをセッションから取り出し
    scroll_to_editor = session.pop("scroll_to_editor", False)

    # レコードセットをテンプレートに渡す
    return render_template(
        "pages/index.html", 
        columns=columns, 
        rows=rows, 
        table_names=db.TABLE_NAMES, 
        sql_query=sql_query, 
        sql_query_height=sql_query_height, 
        scroll_to_editor=scroll_to_editor
    )

# 各テーブルの構造データ（JSON）を返すWeb API
@app.route("/api/table/<table_name>")
def api_table_structure(table_name):
    allowed_tables = db.TABLE_NAMES
    if table_name not in allowed_tables:
        # JSONとステータスコード（`400`: Bad Request）を返す
        return {"error": "Invalid table name"}, 400
    # `fields`: カラム名のリスト
    # `values`: `Row`オブジェクトのリスト
    # fields, values = db.describe_table(table_name)
    fields, values = db_excel.describe_table(table_name)
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
    sql_query = ''
    columns = []
    rows = []
    scroll_to_editor = False

    if request.method == 'POST':
        sql_query = request.form.get('sql_query', '')
        # DBにクエリを投げてレコードセットを取得する処理
        # 後で書く
        # 実験用ダミーレコードセット
        columns = ['id', 'name', 'score']
        rows = [
            [1, 'James', 90], 
            [2, 'Lars', 75], 
        ]
        scroll_to_editor = True
    else:
        # セッションに保存した直近のクエリをテンプレートに渡す
        sql_query = session.pop("last_posted_query", "")
        # デフォルトの擬似テーブルを表示
        columns, rows = [DEFAULT_COLUMNS, DEFAULT_ROWS]

    # エディタの高さ情報をセッションから取り出し
    sql_query_height = session.get("sql_query_height", DEFAULT_EDITOR_HEIGHT)
    # エディタへのスクロールフラグをセッションから取り出し
    scroll_to_editor = session.pop("scroll_to_editor", False)
    
    return render_template(
        'pages/playground.html', 
        columns=columns, 
        rows=rows, 
        table_names=db.TABLE_NAMES,
        sql_query=sql_query, 
        sql_query_height=sql_query_height, 
        scroll_to_editor=scroll_to_editor
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
    # fields, values = db.describe_table(table_name)
    fields, values = db_excel.describe_table(table_name)

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
