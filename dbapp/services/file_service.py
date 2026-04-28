import os
import re
from datetime import datetime
import pyodbc
from typing import List, Tuple, Optional, Any
from pathlib import Path
import uuid
import json

# 結果セット一時保存用
TMP_DIR = Path(__file__).resolve().parent.parent / "storage" / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

def save_query_to_file(sql_query: str, user_filename: str, storage_dir: str) -> Tuple[Optional[str], str, str]:
    """ SQLクエリを`.sql`ファイルとして保存する

    :param sql_query: SQLのクエリ文字列
    :type sql_query: str
    :param user_filename: ユーザが入力したファイル名（ベース名）
    :type user_filename: str
    :param storage_dir: 保存先ディレクトリのパス（文字列）
    :type storage_dir: str
    :return: ファイル名・成功/失敗メッセージ・メッセージカテゴリのタプル
    :rtype: Tuple[Optional[str], str, str]

    .. note::
        - `.sql`ファイルの保存先は`storage/queries`
        - `category`は`success` or `error`
    
    .. warning::
        - 特になし

    .. hint::
        - services/file_service.py

    .. important::
        - 特になし
    """
    if not (sql_query and sql_query.strip()):
        return None, "( ´,_ゝ｀) < クエリが空のため、保存できません。", "error"
    
    if user_filename and user_filename.strip():
        safe_name = re.sub(r'[\/\\:\*\?h"<>\|]', '_', user_filename.strip())
    else:
        safe_name = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    filename = f"{safe_name}.sql"

    # storage_dirをPathオブジェクト化
    storage_path = Path(storage_dir)
    storage_path.mkdir(parents=True, exist_ok=True)
    
    path = storage_path / filename

    # ファイル書き込み
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(sql_query)

    return filename, "クエリを`.sql`ファイルとして保存しました。: ", "success"

