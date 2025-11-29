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

SELECT_ANSWER_QUERY = """
    SELECT
        q.AnswerQuery
        , q.CheckMode
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

EXISTS_QUESTION_QUERY = """
    SELECT
        1
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
# 編集用に問題・正解のセットを取得するクエリ
SELECT_QUESTION_DATA_QUERY = """
    SELECT
        q.ChapterNumber
        , q.SectionNumber
        , q.QuestionNumber
        , q.Question
        , q.AnswerQuery
        , q.CheckMode
        , c.ChapterTitle
        , s.SectionTitle
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
        q.ChapterNumber = ?
        AND q.SectionNumber = ?
        AND q.QuestionNumber = ?
    ;
"""

# 問題データ更新用クエリ
UPDATE_QUESTION_QUERY = """
    UPDATE Questions
    SET
        Question = ?
        , AnswerQuery = ? 
        , CheckMode = ?
    WHERE
        ChapterNumber = ?
        AND SectionNumber = ?
        AND QuestionNumber = ?
    ;
"""

def fetch_all(sql_query: str, params: Optional[Sequence[Any]]=None) -> Tuple[List[str], List[Dict[str, Any]]]:
    """ 複数のレコードセットを取得する
    """
    if params is None:
        params = ()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql_query, params)
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

def get_question_data(chapter_number: int, section_number: int, question_number):
    return fetch_one(SELECT_QUESTION_DATA_QUERY, (chapter_number, section_number, question_number))

def update_question(chapter_number:int, section_number: int, question_number: int, question_text: str, answer_query: str, check_mode: str = "strict"):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            UPDATE_QUESTION_QUERY, 
            (question_text, answer_query, check_mode, chapter_number, section_number, question_number)
        )
        if cur.rowcount == 0:
            raise ValueError("指定の問題が存在しません。")
        conn.commit()
