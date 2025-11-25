from dbapp.db import queries as dbq
from dbapp.db import import_from_excel as db_excel
from typing import Tuple, List, Dict, Any, Sequence, Literal, Optional

from dbapp.db.exceptions import (
    DatabaseExecutionError, 
    QuerySyntaxError, 
    QueryRuntimeError
)

import pyodbc
from .query_compare.messages import CompareResult

def compare_queries(
    user_query: str, 
    answer_query: str, 
    check_mode: Literal["strict", "loose", "custom"] = "strict", 
    rule: Optional[dict] = None, 
    use_excel: bool=False
) -> Tuple[bool, CompareResult, str, dict[str, Any], List[str], List[pyodbc.Row], List[str], List[pyodbc.Row]]:
    """ 2つのクエリを受け取って結果を比較する
        Returns:
        result(bool): 正解 / 不正解
        message(str): エラーメッセージ（成功時は空）
        detail(dict): 比較の詳細情報
    """
    result = False
    result_enum = None
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
        return result, result_enum, message, detail, user_columns, user_rows, answer_columns, answer_rows

    # ユーザークエリと正解クエリを実行して結果を取得
    # ユーザークエリ・正解クエリの実行結果を取得
    #   -> 例外発生時はキャッチしてRuntimeErrorをスロー
    try:
        user_columns, user_rows = _safe_fetch_all(query=cleansed_query, role=query_role_user, params=None, use_excel=use_excel)
        answer_columns, answer_rows = _safe_fetch_all(query=answer_query, role=query_role_answer, params=None, use_excel=use_excel)
    except RuntimeError as e:
        return False, result_enum, str(e), {}, user_columns, user_rows, answer_columns, answer_rows
    
    # ユーザクエリの結果セットと正解クエリの結果セットをタプルにする
    user_result = (user_columns, user_rows)
    answer_result = (answer_columns, answer_rows)

    if check_mode == "strict":
        result, result_enum, message, detail = _compare_result_strict(
            user_result=user_result, 
            answer_result=answer_result
        )
    elif check_mode == "loose":
        pass
    else:
        pass
    return result, result_enum, message, detail, user_columns, user_rows, answer_columns, answer_rows

def _safe_fetch_all(query: str, role: str, params: Optional[Sequence[Any]]=None, use_excel=False) -> Tuple[List[str], List[pyodbc.Row]]:
    try:
        if use_excel:
            return db_excel.fetch_all_excel(query=query, params=params)
        else:
            return dbq.fetch_all(query=query, params=params)
    except QuerySyntaxError as e:
        raise RuntimeError(f"{role}（SQL構文エラー）: {e}") from e
    except QueryRuntimeError as e:
        raise RuntimeError(f"{role}（SQL実行時エラー）: {e}") from e
    except DatabaseExecutionError as e:
        raise RuntimeError(f"{role}（DBエラー）: {e}") from e
    
from .query_compare.messages import (
    CompareResult, 
    COMPARE_RESULT_MESSAGES
)
from .query_compare.strict import compare_strict

def _compare_result_strict(
        user_result: Tuple[List[str], List[pyodbc.Row]], 
        answer_result: Tuple[List[str], List[pyodbc.Row]]
        ) -> Tuple[bool, str, Dict[str, Any]]:
    result_enum, detail = compare_strict(user_result=user_result, answer_result=answer_result)
    message = COMPARE_RESULT_MESSAGES[result_enum]

    result = (result_enum == CompareResult.OK)
    return result, result_enum, message, detail