from flask import (
    Flask, render_template, abort, request, flash, redirect, 
    url_for, session)
from dotenv import load_dotenv
# import pyodbc

from dbapp.config import ( 
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
    # エディタのクエリ保存関係
    save_editor_query, pop_editor_query, clear_editor_query, 
    # エディタの高さ関連
    save_query_editor_height, load_query_editor_height, clear_query_editor_height, 
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

# DB接続に踏み台Excelを使うかどうか（`.env`から取得）
using_excel = (os.getenv("USING_EXCEL").upper() == "TRUE")

def _exec_sql_query(sql_query: str, page: str, use_excel: bool=False) -> tuple[list, list]:
    # クエリ実行 -> レコードセット取得
    columns, rows, message, category = exec_query(sql_query=sql_query, use_excel=use_excel)
    # フラッシュメッセージ
    flash(message, category)
    # セッションにスクロールフラグを立てる
    set_scroll_to_editor(page, True)
    # レコードセットを返す
    return columns, rows

def _prepare_exec_query(form, page: str) -> tuple[str, str | None]:
    # クエリ実行の前処理
    sql_query = form.get("sql_query", "").strip()
     # CodeMirrorラッパーの高さを保存
    sql_query_height = request.form.get("sql_query_height")
    if sql_query_height:
        # エディタの高さをセッションに保存
        save_query_editor_height(
            sql_query_height=sql_query_height, 
            page=page, 
        )
    return sql_query, sql_query_height

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
        # クエリ実行準備
        sql_query, sql_query_height = _prepare_exec_query(form=request.form, page="index")
        
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
            save_editor_query(sql_query=sql_query, page="index")
            # セッションにスクロールフラグを立てる
            set_scroll_to_editor(True)
            # トップページにリダイレクト
            return redirect(url_for("index"))
        elif "execute" in request.form:
            # クエリ実行 -> レコードセット取得
            columns, rows = _exec_sql_query(sql_query=sql_query, page="index", use_excel=using_excel)

    # GETリクエストのとき
    else:
        # セッションに保存した直近のクエリをテンプレートに渡す
        sql_query = pop_editor_query("index")
        # デフォルトの擬似テーブルを表示
        columns, rows = [DEFAULT_COLUMNS, DEFAULT_ROWS]

    # エディタの高さ情報をセッションから取り出し
    sql_query_height = load_query_editor_height("index")
    # エディタへのスクロールフラグをセッションから取り出し
    scroll_to_editor = pop_scroll_to_editor("index")

    # レコードセットをテンプレートに渡す
    return render_template(
        "pages/top/index.html", 
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
    if using_excel:
        fields, values = db_excel.describe_table(table_name)
    else:
        fields, values = dbq.describe_table(table_name)
    # Rowオブジェクトをリストに変換してリストのリストにする
    rows_list = [list(row) for row in values]
    # クライアントにJSONを返す
    return {
        "columns": fields, 
        "rows": rows_list, 
    }

from .data.practices import (
    generate_structured_practice_list
)
# 練習問題の一覧を表示するページ
@app.route('/practices', methods=['GET'])
def practices():
    # 問題データ取得
    chapters = generate_structured_practice_list()

    # セッションに記録したエディタの高さ・入力クエリをクリアする
    clear_editor_query(page="practice")
    clear_query_editor_height(page="practice")

    return render_template(
        "pages/practices/index.html", 
        chapters=chapters
    )

from .data.practices import fetch_question

# 練習問題のページ
@app.route('/practices/<int:chapter>/<int:section>/<int:question>', methods=["GET"])
def practice_detail(chapter, section, question):
    # 問題データを取得
    row = fetch_question(
        chapter_number=chapter, 
        section_number=section, 
        question_number=question
    )
    
    # レコードセットがない
    if row is None:
        abort(404, "( ´,_ゝ`)ﾌﾟｯ < 指定された問題がないｗｗｗ")

    # セッションにエディタの高さとクエリがあれば復元
    preserved_query = pop_editor_query(page="practice")
    sql_query_height = load_query_editor_height(page="practice")

    return render_template(
        "pages/practices/practice_detail.html", 
        row=row, 
        table_names=dbq.TABLE_NAMES, 
        sql_query=preserved_query, 
        sql_query_height=sql_query_height
    )

# 正解データ取得用
from dbapp.data import practice_queries as pq
# 正解/不正解判定用
from dbapp.services.practice_service import compare_queries
# 結果表示用データ取得用
from .services.query_compare.messages import (
    CompareResult, 
    COMPARE_RESULT_MESSAGES
)
@app.route('/practices/judge_result', methods=["POST"])
def judge_result():
    """ 答案クエリと正解クエリを受け取って、正誤を判定
        結果表示ページにリダイレクト
    """
    # 章・節・問題番号を取得
    chapter_number = request.form.get("chapter_number")
    section_number = request.form.get("section_number")
    question_number = request.form.get("question_number")
    question_info = (chapter_number, section_number, question_number)

    # 正解クエリとチェックモードを取得
    answer_data = pq.fetch_one(pq.SELECT_ANSWER_QUERY, params=question_info)
    answer_query, checkmode = (answer_data["AnswerQuery"], answer_data["CheckMode"])

    # ユーザが投稿したクエリを取得
    org_user_query = request.form.get("sql_query", "")
    #   併せてエディタの高さをセッションに保存
    user_query, editor_height = _prepare_exec_query(form=request.form, page="practice")
    # エディタのクエリをセッションに保存
    save_editor_query(sql_query=user_query, page="practice")

    # クエリの実行結果を判定
    (
        result, result_enum, message, detail, 
        user_columns, user_rows, 
        answer_columns, answer_rows) = compare_queries(
            user_query=user_query, 
            answer_query=answer_query, 
            check_mode=checkmode, 
            rule=None, 
            use_excel=using_excel
        )

    return render_template(
        "pages/practices/judge_result.html", 
        result=result, 
        result_enum=result_enum, 
        message=message, 
        detail=detail, 
        question_info=question_info,
        user_columns=user_columns, 
        user_rows=user_rows, 
        answer_columns=answer_columns, 
        answer_rows=answer_rows, 
        CompareResult=CompareResult, 
        COMPARE_RESULT_MESSAGES=COMPARE_RESULT_MESSAGES, 
        user_query=org_user_query.strip()
    )

# 問題・正解クエリの編集ページ
@app.route("/questions/edit/<chapter>/<section>/<question>")
def questions_edit():
    pass

# クエリを実行するだけのページ
@app.route('/playground', methods=['GET', 'POST'])
def playground():
    # ローカル変数初期化
    sql_query: str = ''
    columns: list = []
    rows: list = []
    scroll_to_editor: bool = False

    if request.method == 'POST':
        # クエリ実行準備
        sql_query, sql_query_height = _prepare_exec_query(form=request.form, page="playground")
        # クエリ実行 -> レコードセット取得
        columns, rows = _exec_sql_query(sql_query=sql_query, page="playground", use_excel=using_excel)
    else:
        # セッションに保存した直近のクエリをテンプレートに渡す
        sql_query = pop_editor_query("playgcound")
        # デフォルトの擬似テーブルを表示
        columns, rows = [DEFAULT_COLUMNS, DEFAULT_ROWS]

    # エディタの高さ情報をセッションから取り出し
    sql_query_height = load_query_editor_height(page="playground")
    # エディタへのスクロールフラグをセッションから取り出し
    scroll_to_editor = pop_scroll_to_editor(page="playground")
    
    return render_template(
        'pages/_legacy/playground.html', 
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
    print(using_excel)
    # DESC文実行
    if using_excel:
        fields, values = db_excel.describe_table(table_name)
    else:
        fields, values = dbq.describe_table(table_name)
    # fields, values = db_excel.describe_table(table_name)

    # テンプレートにデータを投げる
    return render_template(
        "pages/_legacy/table.html", 
        table_names=allowed_tables, 
        table_name=table_name, 
        columns=fields, 
        rows=values
    )

if __name__ == "__main__":
    app.run(debug=True)
