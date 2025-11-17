from flask import session
from dbapp.config import DEFAULT_EDITOR_HEIGHT

def save_editor_query(sql_query: str, page: str):
    """ エディタのクエリをセッションに保存
    """
    session[f"{page}_last_posted_query"] = sql_query

def pop_editor_query(page: str):
    """ セッションに保存されたクエリを返す
    """
    return session.pop(f"{page}_last_posted_query", "")

def clear_editor_query(page: str):
    """ セッションに保存したクエリをクリアする
    """
    session.pop(f"{page}_last_posted_query", None)

def save_query_editor_height(sql_query_height: str, page: str):
    """ 渡された値をセッションに保存
    """
    try:
        session[f"{page}_sql_query_height"] = float(sql_query_height)
        # 値がおかしかったらデフォルト値をセット
    except ValueError:
        session[f"{page}_sql_query_height"] = DEFAULT_EDITOR_HEIGHT

def load_query_editor_height(page: str):
    # セッションの値を返す
    return session.get(f"{page}_sql_query_height", DEFAULT_EDITOR_HEIGHT)

def clear_query_editor_height(page: str):
    """ セッションに保存したエディタ高さをクリア
    """
    session.pop(f"{page}_sql_query_height", None)

def set_scroll_to_editor(page: str, value: bool=True):
    """ エディタ部分へのスクロールフラグをセット
    """
    session[f"{page}_scroll_to_editor"] = value

def pop_scroll_to_editor(page: str):
    """ スクロールフラグを取り出してクリアする
    """
    return session.pop(f"{page}_scroll_to_editor", False)