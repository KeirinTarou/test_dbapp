from flask import session
from dbapp.config import DEFAULT_EDITOR_HEIGHT
from typing import Any, Tuple, List

from file_service import (
    load_temp_result, delete_temp_result)

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
    

def get_result_from_session() -> (
        Tuple[List[str], List[List[Any]]] | Tuple[None, None]):
    """ セッションから一時ファイルのIDを取り出す
        
    :return: カラム名のリストと各行のデータのリストのリストを詰め込んだタプル
    :rtype: Tuple[List[str]], List[List[Any]]] or Tuple[None, None]
    .. note::
        - 一時ファイルのIDがセッションにないときは、(None, None)が返る
        - file_service.load_temp_result()を呼び出す
    .. warning::
        - 特になし
    .. hint::
        - services/session_service.py
    .. important::
        - 特になし
    """
    temp_id = session.get("last_temp_id")
    if not temp_id:
        return None, None
    return load_temp_result(temp_id)

def delete_result_from_session() -> None:
    """  セッションの一時ファイルのIDを消す
        
    :return: 返り値なし
    :rtype: None
    .. note::
        - file_service.delete_temp_result()を呼び出す
    .. warning::
        - 特になし
    .. hint::
        - services/session_service.py
    .. important::
        - 特になし
    """
    temp_id = session.pop("last_temp_id", None)
    if temp_id: 
        delete_temp_result(temp_id)