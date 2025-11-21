# 練習問題リスト作成用
from itertools import groupby
from operator import itemgetter
from typing import Tuple, List, Dict, Any

from .sqlite_connection import (
    get_connection
)

from .practice_queries import (
    PRACTICES_LIST_QUERY
)


def _exec_query(sql_query: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql_query)
        columns = [col[0] for col in cur.description]
        rows = [dict(row) for row in cur.fetchall()]
    return columns, rows

def generate_structured_practice_list() -> List[Dict[str, Any]]:
    """ 練習問題リスト作成
        章 -> 節 -> 問題の階層を作る
    """
    # 問題データを全取得
    _, rows = _exec_query(sql_query=PRACTICES_LIST_QUERY)

    # 章 -> 節 -> 問題 のネスト構造を構築
    chapters = []
    # 章番号グループをループ
    for chapter_number, chapter_group in groupby(rows, key=itemgetter("ChapterNumber")):
        chapter_rows = list(chapter_group)
        # タイトルは、同じ章の中で共通なので、先頭レコードの値を採る
        chapter_title = chapter_rows[0]["ChapterTitle"]
        sections = []
        # 章内の節グループをループ
        for section_number, section_group in groupby(chapter_rows, key=itemgetter("SectionNumber")):
            section_rows = list(section_group)
            section_title = section_rows[0]["SectionTitle"]
            sections.append({
                "section_number": section_number, 
                "section_title": section_title, 
                "questions": section_rows
            })
        chapters.append({
            "chapter_number": chapter_number, 
            "chapter_title": chapter_title, 
            "sections": sections
        })

    return chapters