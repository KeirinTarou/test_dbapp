from typing import List, Tuple, Dict, Any
from enum import Enum
import pyodbc
from itertools import islice

from .messages import CompareResult, COMPARE_RESULT_MESSAGES

def compare_strict(
    user_result: Tuple[List[str], List[pyodbc.Row]], 
    answer_result: Tuple[List[str], List[pyodbc.Row]]
) -> Tuple[CompareResult, Dict[str, Any]]:
    """ 'strict'モードでの比較
        差分を調べ、CompareResultとdetail（dict）で返す
        dictは、不一致の詳細
    """
    # ユーザが投稿したクエリ、正解クエリそれぞれの結果セットを取得
    user_columns, user_rows = user_result
    answer_columns, answer_rows = answer_result

    # 列数チェック
    if len(user_columns) != len(answer_columns):
        return CompareResult.COLUMN_COUNT_MISMATCH, {
            "user_columns": user_columns, 
            "answer_columns": answer_columns, 
        }
    
    # 列名チェック
    if user_columns != answer_columns:
        return CompareResult.COLUMN_NAME_MISMATCH, {
            "user_columns": user_columns, 
            "answer_columns": answer_columns, 
        }
    
    # 行数チェック
    if len(user_rows) != len(answer_rows): 
        return CompareResult.ROW_COUNT_MISMATCH, {
            "user_rows": len(user_rows), 
            "answer_rows": len(answer_rows), 
        }
    
    # 行の順序チェック
    user_list = _rows_to_list(user_rows)
    answer_list = _rows_to_list(answer_rows)

    if user_list != answer_list:
        # 順番違いであるかどうか判定
        #   ソートしたら一致する -> 順番だけが違う
        if sorted(user_list) == sorted(answer_list):
            return CompareResult.ROW_ORDER_MISMATCH, {
                "user_rows": user_list, 
                "answer_rows": answer_list, 
            }
        else:
            # 順番違いだけが原因ではない
            #   -> 中身が異なる
            # Setを用いて差分を取得
            user_set = set(user_list)
            answer_set = set(answer_list)
            # 不足レコードと過剰レコード
            missing = list(islice(answer_set - user_set, 3))
            extra = list(islice(user_set - answer_set, 3))

            return CompareResult.ROW_CONTENT_MISMATCH, {
                "user_rows": user_list, 
                "answer_rows": answer_list, 
                "missing": missing, 
                "extra": extra, 
            }
    
    # ここまでたどり着いたら完全一致 -> 正解
    return CompareResult.OK, {}

def _rows_to_list(rows: List[pyodbc.Row]) -> List[Tuple[Any, ...]]:
    """ pyodbc.Rowオブジェクトをタプルに変換して比較可能にする
    """
    return [tuple(row) for row in rows]