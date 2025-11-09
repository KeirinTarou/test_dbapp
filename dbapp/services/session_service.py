from flask import session
from dbapp.config import DEFAULT_EDITOR_HEIGHT

def save_query_editor_height(sql_query_height):
    """ 渡された値をセッションに保存
    """
    try:
        session["sql_query_height"] = float(sql_query_height)
        # 値がおかしかったらデフォルト値をセット
    except ValueError:
        session["sql_query_height"] = DEFAULT_EDITOR_HEIGHT

def load_query_editor_height():
    # セッションの値を返す
    return session.get("sql_query_height", DEFAULT_EDITOR_HEIGHT)