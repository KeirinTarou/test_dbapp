# 練習問題リスト作成用
from itertools import groupby
from operator import itemgetter

from typing import List, Dict, Any, Optional

from .practice_queries import (
    PRACTICES_LIST_QUERY, 
    fetch_all, 
    SELECT_QUESTION, 
    fetch_one
)

def generate_structured_practice_list() -> List[Dict[str, Any]]:
    """ 練習問題リスト作成
        章 -> 節 -> 問題の階層を作る
    """
    # 問題データを全取得
    _, rows = fetch_all(sql_query=PRACTICES_LIST_QUERY)

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

def fetch_question(chapter_number: int, section_number: int, question_number: int) -> Optional[Dict[str, Any]]:
    """ 問題データ取得
    """
    params = (chapter_number, section_number, question_number)
    return fetch_one(sql_query=SELECT_QUESTION, params=params)