from dbapp.db.connection import get_connection
import re

from typing import (
    Any, Dict, Iterable, List, Optional, 
    Sequence, Tuple
)
import pyodbc

from .exceptions import (
    DatabaseExecutionError, 
    QuerySyntaxError, 
    QueryRuntimeError
)

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

SELECT_ANSWER_QUERY = """
    SELECT
        q.AnswerQuery
        , q.CheckMode
    FROM
        Questions AS q
        JOIN
            Chapters AS c
            ON c.ChapterID = q.ChapterID
        JOIN
            Sections AS s
            ON s.SectionID = q.SectionID
    WHERE
        c.ChapterNumber = ?
        AND s.SectionNumber = ?
        AND q.QuestionNumber = ?
    ;
"""

INSERT_QUESTION_QUERY = """
    INSERT INTO Questions (
        ChapterID
        , SectionID
        , QuestionNumber
        , Question
        , AnswerQuery
        , CheckMode
    ) VALUES (
        ?
        , ?
        , ?
        , ?
        , ?
        , ?
    )
"""

EXISTS_QUESTION_QUERY = """
    SELECT
        1
    FROM
        Questions AS q
        JOIN
            Chapters AS c
            ON c.ChapterID = q.ChapterID
        JOIN
            Sections AS s
            ON s.SectionID = q.SectionID
    WHERE
        c.ChapterNumber = ?
        AND s.SectionNumber = ?
        AND q.QuestionNumber = ?
    ;
"""

TABLE_NAMES = [
    "BelongTo", "Categories", "CustomerClasses", "Customers", 
    "Departments", "Employees", "Prefecturals", "Products", 
    "Salary", "Sales"
]

import sqlparse
from sqlparse.sql import Identifier, TokenList
from sqlparse.tokens import Keyword, DML, DDL
FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", 
    "CREATE", "TRUNCATE", "GRANT", "REVOKE", "MERGE", 
    "REPLACE"
}

def insert_question(
        chapter_number: int, 
        section_number: int, 
        question_number: int, 
        question_text: str, 
        answer_query: str, 
        check_mode: str = "strict"
) -> bool:
    sql_query = INSERT_QUESTION_QUERY
    params = (
        chapter_number, 
        section_number, 
        question_number, 
        question_text, 
        answer_query, 
        check_mode
    )
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query, params)
            # 変更をコミット
            conn.commit()
            return True
    # DB由来の例外をキャッチ
    except pyodbc.ProgrammingError as e:
        # SQLの構文エラーはここでキャッチ -> スロー
        raise QuerySyntaxError("db/queries/insert_query(): " + str(e)) from e
        return False
    except pyodbc.Error as e:
        raise QueryRuntimeError("db/queries/insert_query(): " + str(e)) from e
        return False

def exists_question(
    chapter_number: int, 
    section_number: int, 
    question_number: int
) -> bool:
    sql_query = EXISTS_QUESTION_QUERY
    params = (chapter_number, section_number, question_number)
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query, params)
                return cur.fetchone() is not None
    except Exception:
        return False

def fetch_one(query: str, params: Optional[Sequence[Any]]=None) -> Optional[Dict[str, Any]]:
    if params is None:
        params = ()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)

                columns = [col[0] for col in cur.description]
                row = cur.fetchone()

                # 結果セットが返らなかったらNone
                if row is None:
                    return None
                # 取得した1件のレコードをdictにして返す
                return dict(zip(columns, row))
        
    # DB由来の例外をキャッチ
    except pyodbc.ProgrammingError as e:
        # SQLの構文エラーはここでキャッチ -> スロー
        raise QuerySyntaxError(str(e)) from e
    except pyodbc.Error as e:
        raise QueryRuntimeError(str(e)) from e
        

def fetch_all(query: str, params: Optional[Sequence[Any]]=None) -> Tuple[List[str], List[pyodbc.Row]]:
    """ クエリを渡して全件取得する
        カラム名（str）のリスト, Rowオブジェクトのリストを返す
    """
    if params is None:
        params = ()
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                # カラム名のリストを取得
                columns = [col[0] for col in cur.description]
                # レコードセットを取得（`pyodbc.Row`オブジェクトのリスト）
                rows = cur.fetchall()
                # カラム名のリストと`Row`オブジェクトのリストを返却
                return columns, rows
    
    # DB由来の例外をキャッチ
    except pyodbc.ProgrammingError as e:
        # SQLの構文エラーはここでキャッチ -> スロー
        raise QuerySyntaxError(str(e)) from e
    except pyodbc.Error as e:
        raise QueryRuntimeError(str(e)) from e


def describe_table(table_name: str) -> Tuple[List[str], List[pyodbc.Row]]:
    """ `DESC`コマンドを使ってテーブル構造を取得
    """
    query = f"DESC {table_name};"
    return fetch_all(query)

def sanitize_sql(sql_query: str) -> str:
    """ SQL文からコメントや不要な空白を除去する
    """
    # ブロックコメント削除
    sql = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)
    # 行コメント削除
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    # 前後の空白除去
    return sql.strip()

def contains_forbidden_keywords(sql_query: str) -> bool:
    """ 禁止キーワードが含まれているかどうかを返す
    """
    parsed = sqlparse.parse(sql_query)

    def check_tokens(tokens):
        for token in tokens:
            if getattr(token, "is_group", False):
                if check_tokens(token.tokens):
                    return True
            elif token.ttype in (Keyword, DML, DDL):
                if token.value.upper() in FORBIDDEN_KEYWORDS:
                    return True
        return False
    
    for stmt in parsed:
        if check_tokens(stmt.tokens):
            return True
    return False

def is_multi_statement(sql_query: str) -> bool:
    """ 実質的なSQL文が2つ以上あるかどうか
    """
    statements = [stmt for stmt in sqlparse.split(sql_query) if stmt.strip()]
    return len(statements) > 1

def _validate_sql_core(sql_query: str, allowed_start=("SELECT", )) -> Tuple[bool, str, str]:
    """ 検査結果とエラーメッセージ、サニタイズ済みクエリを返す
        合格時はTrueとNone、サニタイズ済みクエリを返す
    """
    clean_sql = sanitize_sql(sql_query)

    if not clean_sql:
        return False, "有効なクエリがありません。", clean_sql

    upper = clean_sql.upper()
    if not any(upper.startswith(kw) for kw in allowed_start):
        return False, f"{', '.join(allowed_start)}文のみ実行可能です。", clean_sql
    
    if contains_forbidden_keywords(clean_sql):
        return False, "書き込み系・DDL文は使用禁止です。", clean_sql
    
    if is_multi_statement(sql_query=clean_sql):
        return False, "マルチステートメントは使用禁止です。", clean_sql 

    return True, None, clean_sql

def valid_sql(sql_query: str, allowed_start=("SELECT", )) -> bool:
    """ SQL文が安全かどうかを判定する
        先頭キーワードが`allowed_start`のいずれかであることをチェック
        禁止キーワードが含まれていないかチェック
        コメントや空白は無視して判定
    """
    ok, _, _ = _validate_sql_core(sql_query=sql_query, allowed_start=allowed_start)
    return ok

def sanitize_and_validate_sql(sql_query: str, allowed_start=("SELECT", )) -> str:
    """ サニタイズとバリデーションをまとめて行う
        不正があれば例外をスロー
    """
    ok, message, clean_sql = _validate_sql_core(sql_query=sql_query, allowed_start=allowed_start)
    
    if not ok:
        raise ValueError(message)

    return clean_sql