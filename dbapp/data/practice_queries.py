from typing import Tuple, List, Dict, Any, Optional, Sequence

from .sqlite_connection import (
    get_connection
)

PRACTICES_LIST_QUERY = """
SELECT
    c.ChapterNumber
    , c.ChapterTitle
    , s.SectionNumber
    , s.SectionTitle
    , q.*
FROM
    Questions AS q
    JOIN
        Chapters AS c
        ON c.ChapterNumber = q.ChapterNumber
    JOIN
        Sections AS s
        ON s.SectionNumber = q.SectionNumber
        AND s.ChapterNumber = q.ChapterNumber
ORDER BY
    c.ChapterNumber ASC
    , s.SectionNumber ASC
    , q.QuestionNumber ASC
;
"""

SELECT_QUESTION = """
SELECT
    c.ChapterNumber
    , c.ChapterTitle
    , s.SectionNumber
    , s.SectionTitle
    , q.QuestionNumber
    , q.Question
FROM
    Questions AS q
    JOIN
        Chapters AS c
        ON c.ChapterNumber = q.ChapterNumber
    JOIN
        Sections AS s
        ON s.SectionNumber = q.SectionNumber
        AND s.ChapterNumber = q.ChapterNumber
WHERE
    c.ChapterNumber = ?
    AND s.SectionNumber = ?
    AND q.QuestionNumber = ?
;
"""

def fetch_all(sql_query: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """ 複数のレコードセットを取得する
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql_query)
        columns = [col[0] for col in cur.description]
        rows = [dict(row) for row in cur.fetchall()]
    return columns, rows

def fetch_one(sql_query: str, params: Optional[Sequence[Any]]=None) -> Optional[Dict[str, Any]]:
    """ 結果を1件だけ返す
    """
    if params is None:
        params = ()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql_query, params)
        columns = [col[0] for col in cur.description]
        row = cur.fetchone()
        # 結果が取得できなかったらNoneを返す
        if row is None:
            return None
        # 取得した1件のレコードセットをDictにして返す
        return dict(zip(columns, row))