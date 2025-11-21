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

