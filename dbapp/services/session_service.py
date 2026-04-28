from flask import session
from dbapp.config import DEFAULT_EDITOR_HEIGHT
from typing import Any, Tuple, List, Optional

from file_service import load_temp_result

def save_editor_query(sql_query: str, page: str):
    """ エディタのクエリをセッションに保存
        services/session_service
    """
    session[f"{page}_last_posted_query"] = sql_query

def pop_editor_query(page: str):
    """ セッションに保存されたクエリを返す
        services/session_service
    """
    return session.pop(f"{page}_last_posted_query", "")

def clear_editor_query(page: str):
    """ セッションに保存したクエリをクリアする
        services/session_service
    """
    session.pop(f"{page}_last_posted_query", None)

def save_query_editor_height(sql_query_height: str, page: str):
    """ 渡された値をセッションに保存
        services/session_service
    """
    try:
        session[f"{page}_sql_query_height"] = float(sql_query_height)
        # 値がおかしかったらデフォルト値をセット
    except ValueError:
        session[f"{page}_sql_query_height"] = DEFAULT_EDITOR_HEIGHT

def load_query_editor_height(page: str):
    """ セッションの値を返す
        services/session_service
    """
    return session.get(f"{page}_sql_query_height", DEFAULT_EDITOR_HEIGHT)

def clear_query_editor_height(page: str):
    """ セッションに保存したエディタ高さをクリア
        services/session_service
    """
    session.pop(f"{page}_sql_query_height", None)

def set_scroll_to_editor(page: str, value: bool=True):
    """ エディタ部分へのスクロールフラグをセット
        services/session_service
    """
    session[f"{page}_scroll_to_editor"] = value

def pop_scroll_to_editor(page: str):
    """ スクロールフラグを取り出してクリアする
        services/session_service
    """
    return session.pop(f"{page}_scroll_to_editor", False)

def save_result_to_session(temp_id: str) -> None:
    """ クエリの実行結果を保存した一時ファイルのIDをセッションに保存する

    :param tmp_id: 一時ファイルのUUID
    :type tmp_id: str
    :return: 返り値なし
    :rtype: None
    .. note::
        - 特になし
    .. warning::
        - 特になし
    .. hint::
        - services/session_service.py
    .. important::
        - 特になし
    """
    session["last_temp_id"] = temp_id
    

def pop_result_from_session():
    """ セッションから結果を取り出す
        services/session_service
    """
    columns = session.pop("result_columns", None)
    rows = session.pop("result_rows", None)
    return columns, rows