class DatabaseExecutionError(Exception):
    """ DB実行時の一般的エラー
    """
    pass

class QuerySyntaxError(DatabaseExecutionError):
    """ SQL構文エラー
    """
    pass

class QueryRuntimeError(DatabaseExecutionError):
    """ 接続・タイムアウト・ロックなどの実行時エラー
    """
    pass
