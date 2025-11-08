import os
import re
from datetime import datetime
from typing import Tuple, Optional

def save_query_to_file(sql_query: str, user_filename: str, storage_dir: str) -> Tuple[Optional[str], str, str]:
    """ SQLクエリを`.sql`ファイルとして保存する
        @return: (filename or None, message, category)
            `category`: "success" or "error"
    """
    if not (sql_query and sql_query.strip()):
        return None, "( ´,_ゝ｀) < クエリが空のため、保存できません。", "error"
    
    if user_filename and user_filename.strip():
        safe_name = re.sub(r'[\/\\:\*\?h"<>\|]', '_', user_filename.strip())
    else:
        safe_name = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    filename = f"{safe_name}.sql"
    os.makedirs(storage_dir, exist_ok=True)
    path = os.path.join(storage_dir, filename)

    # ファイル書き込み
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(sql_query)

    return filename, f"クエリを`.sql`ファイルとして保存しました。: ", "success"