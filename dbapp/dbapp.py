from flask import (
    Flask, render_template, abort, request, flash, redirect, 
    url_for, session)
import pyodbc
import db.queries as db

app = Flask(__name__)

# セッション用の秘密鍵設定
app.secret_key = "kps"

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
        sql_query_height = request.form.get("sql_query", "")
        if sql_query_height:
            try:
                session["sql_query_height"] = float(sql_query_height)
                # 値がおかしかったらデフォルト値をセット
            except ValueError:
                session["sql_query_height"] = DEFAULT_EDITOR_HEIGHT 

        # クエリ実行 -> レコードセット取得
        try:
            safe_query = db.sanitize_and_validate_sql(sql_query)
            columns, rows = db.fetch_all(safe_query)
            # クエリ実行成功のフラッシュメッセージ
            flash("クエリは正常に実行されました。", "success")
        # `ValueError`例外をキャッチ
        except ValueError as e:
            # 例外発生時のフラッシュメッセージ
            flash(str(e), "error")
            columns, rows = [], []
        except Exception as e:
            # 例外発生時のフラッシュメッセージ
            flash("( ´,_ゝ`) < クエリ実行に失敗しました。", "error")
            columns = FAILED_COLUMNS
            rows = FAILED_ROWS.copy()
            # エラー情報を追加
            rows.append(["原因はたぶん……", str(e)[:200] + "..."])
        # return redirect(url_for("index"))
    # GETリクエストのとき
    else:
        sql_query = ""
        # デフォルトの擬似テーブルを表示
        columns, rows = [DEFAULT_COLUMNS, DEFAULT_ROWS]

    sql_query_height = session.get("sql_query_height", DEFAULT_EDITOR_HEIGHT)
    # レコードセットをテンプレートに渡す
    return render_template(
        "pages/index.html", 
        columns=columns, 
        rows=rows, 
        table_names=db.TABLE_NAMES, 
        sql_query=sql_query, 
        sql_query_height=sql_query_height
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
