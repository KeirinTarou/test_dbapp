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

def save_temp_result(columns: List[str], rows: List[pyodbc.Row]) -> str:
    """ 結果セットを一時ファイルに保存し、ファイルID（UUID）を返す

    :param columns: カラム名のリスト
    :type columns: List[str]
    :param rows: pyodbc.Rowオブジェクトのリスト
    :type rows: List[pyodbc.Row]
    :return: 一時ファイルのファイルID
    :rtype: str

    .. note::
        - 保存先ディレクトリは`storage/tmp`

    .. warning::
        - 特になし

    .. hint::
        - services/file_service.py

    .. important::
        - 特になし
    """
    tmp_id = str(uuid.uuid4())
    path = TMP_DIR / f"{tmp_id}.json"

    # pyodbc.Rowオブジェクトをリスト化
    safe_rows = [list(r) for r in rows]

    with path.open("w", encoding="utf-8") as f:
        # "columns"、"rows"をキーとし、
        # リスト`columns`、`safe_rows`をそれぞれバリューとする
        # dictをJSON形式にエンコードしてファイルに書き込む
        json.dump({"columns": columns, "rows": safe_rows}, f)

    return tmp_id

def load_temp_result(tmp_id: str) -> Tuple[List[str], List[List[Any]]]:
    """ 一時ファイルから結果セットを読み込む

    :param tmp_id: 一時ファイルのUUID
    :type tmp_id: str
    :return: カラム名のリストと各行のデータのリストのリスト
    :rtype: Tuple[List[str], List[List[Any]]]
    
    .. note::
        - 特になし

    .. warning::
        - 特になし

    .. hint::
        - services/file_service.py

    .. important::
        - 特になし
    """
    # 一時ファイルのパスを構築
    path = TMP_DIR / f"{tmp_id}.json"
    # 読み出しモードで開いて変数`f`にぶち込む
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("columns"), data.get("rows")

