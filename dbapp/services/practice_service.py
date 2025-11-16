from dbapp.db import queries as dbq
from typing import Tuple, List, Dict, Any, Sequence, Literal, Optional

from dbapp.config import (
    FAILED_COLUMNS, 
    FAILED_ROWS, 
)

from dbapp.db.exceptions import (
    DatabaseExecutionError, 
    QuerySyntaxError, 
    QueryRuntimeError
)

import pyodbc

def compare_queries(
    user_query: str, 
    answer_query: str, 
    check_mode: Literal["strict", "loose", "custom"] = "strict", 
    rule: Optional[dict] = None
) -> Tuple[bool, str, dict[str, Any]]:
    """ 2つのクエリを受け取って結果を比較する
        Returns:
        result(bool): 正解 / 不正解
        message(str): エラーメッセージ（成功時は空）
        detail(dict): 比較の詳細情報
    """
    result = False
    message = ""
    detail = {}
    user_columns = []
    user_rows = []
    answer_columns = []
    answer_rows = []

    # ユーザークエリのチェック
    # そもそもクエリがおかしかったらreturn
    query_role_user = "ユーザー投稿クエリ"
    query_role_answer = "正解クエリ"
    try:
        cleansed_query = dbq.sanitize_and_validate_sql(sql_query=user_query, allowed_start=("SELECT", "WITH"))
    except ValueError as e:
        result, message, detail = False, f"{query_role_user}: {e}", {}
        return result, message, detail, user_columns, user_rows, answer_columns, answer_rows

    # ユーザークエリと正解クエリを実行して結果を取得
    # ユーザークエリ・正解クエリの実行結果を取得
    #   -> 例外発生時はキャッチしてRuntimeErrorをスロー
    try:
        user_columns, user_rows = _safe_fetch_all(query=cleansed_query, role=query_role_user, params=None)
        answer_columns, answer_rows = _safe_fetch_all(query=answer_query, role=query_role_answer, params=None)
    except RuntimeError as e:
        return False, str(e), {}, user_columns, user_rows, answer_columns, answer_rows
    
    # ユーザクエリの結果セットと正解クエリの結果セットをタプルにする
    user_result = (user_columns, user_rows)
    answer_result = (answer_columns, answer_rows)

    if check_mode == "strict":
        result, message, detail = _compare_result_strict(user_result=user_result, answer_result=answer_result)
    elif check_mode == "loose":
        pass
    else:
        pass
    return result, message, detail, user_columns, user_rows, answer_columns, answer_rows

def _safe_fetch_all(query: str, role: str, params: Optional[Sequence[Any]]=None)  -> Tuple[List[str], List[pyodbc.Row]]:
    try:
        return dbq.fetch_all(query=query, params=params)
    except QuerySyntaxError as e:
        raise RuntimeError(f"{role}（SQL構文エラー）: {e}") from e
    except QueryRuntimeError as e:
        raise RuntimeError(f"{role}（SQL実行時エラー）: {e}") from e
    except DatabaseExecutionError as e:
        raise RuntimeError(f"{role}（DBエラー）: {e}") from e



def _compare_result_strict(
        user_result: Tuple[List[str], List[pyodbc.Row]], 
        answer_result: Tuple[List[str], List[pyodbc.Row]]
        ) -> Tuple[bool, str, Dict[str, Any]]:
    pass