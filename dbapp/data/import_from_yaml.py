import yaml
import sqlite3
import os
from sqlite_connection import (
    get_connection, 
    BASE_DIR, 
    DB_PATH, 
    SRC_PATH
)

# 問題データをインポート
def import_questions(reimport: bool=False):
    # `reimport`フラグがTrueだったら`Question`を空にする
    if reimport:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM Questions;")
            conn.commit()

    yaml_path = os.path.join(SRC_PATH, "questions.yaml")

    # yamlのデータを読み込む
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    success = 0
    fail = 0
    skipped = 0

    for item in data:
        try:
            if insert_question(item):
                success += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"( ´,_ゝ`) < Failed: {e} : {item}")
            fail += 1        

    print(f"( ´_ゝ`) < 全 {success} 件追加しました。")
    print(f"( ´,_ゝ`) < 全 {fail} 件失敗しましたｗｗｗ")
    print(f"(ﾟдﾟ)､ﾍﾟｯ < 全 {skipped} 件スキップしました。")

def insert_question(item) -> bool:
    # 既存の章・節・問番号だったら追加しない
    chapter_number = item["chapter_number"]
    section_number = item["section_number"] 
    question_number = item["question_number"]
    
    if exists_question(
        chapter_number, 
        section_number, 
        question_number
    ):
        return False
    
    conn = get_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO Questions(
            ChapterNumber,
            SectionNumber,
            QuestionNumber,
            Question,
            AnswerQuery,
            CheckMode
        ) VALUES (
            ?, ?, ?, ?, ?, ?
        );
    """

    cur.execute(
        query, 
        (
            chapter_number, 
            section_number, 
            question_number, 
            item["question"], 
            item["answer_query"], 
            item.get("check_mode", "strict")
        )
    )

    conn.commit()
    conn.close()
    return True


def exists_question(chapter_number: int, section_number: int, question_number: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            1
        FROM
            Questions
        WHERE
            ChapterNumber = ?
            AND SectionNumber = ?
            AND QuestionNumber = ?
        LIMIT
            1
        ;
    """, 
    (chapter_number, section_number, question_number)
    )

    row = cur.fetchone()
    conn.close()

    return row is not None

def initial_import():
    # 章データ・節データのインポート
    chapters_yaml = os.path.join(SRC_PATH, "chapters.yaml")
    chapters_query = """
        INSERT INTO chapters (
            ChapterNumber
            , ChapterTitle
        ) VALUES (
            ?, ?
        );
    """
    conn = get_connection()
    cur = conn.cursor()
    # chapters_yamlのデータを読み込む
    with open(chapters_yaml, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        for item in data:
            cur.execute(chapters_query,
                (
                    item["chapter_number"], 
                    item["chapter_title"]
                )
            )
    conn.commit()
    
    sections_yaml = os.path.join(SRC_PATH, "sections.yaml")
    sections_query = """
        INSERT INTO sections (
            SectionNumber, 
            ChapterNumber, 
            SectionTitle
        ) VALUES (
            ?, ?, ?
        );
    """
    # chapters_yamlのデータを読み込む
    with open(sections_yaml, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        for item in data:
            cur.execute(sections_query,
                (
                    item["section_number"], 
                    item["chapter_number"], 
                    item["section_title"]
                )
            )
    conn.commit()
    conn.close() 

# def _get_connection() -> sqlite3.Connection:
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("PRAGMA foreign_keys = ON;")
#     return conn

# エントリポイント
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Import YAML -> SQLite for practice questions")
    parser.add_argument("--init-db", action="store_true", help="Initialize DB from schema.sql")
    parser.add_argument("--initial", action="store_true", help="Import chapters and sections")
    parser.add_argument("--questions", action="store_true", help="Import questions")
    parser.add_argument("--questions-reset", action="store_true", help="Delete all existing questions before importing")
    parser.add_argument("--all", action="store_true", help="Import initial data and questions")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to DB; only simulate")

    args = parser.parse_args()

    # If no flags given, behave like --questions for backwards compatibility
    if not (args.initial or args.questions or args.all):
        args.questions = True

    # `--init_db`オプションありのときはマイグレートを実行
    if args.init_db:
        from migrate import init_db
        init_db()

    # `--dry-run`オプションありのときは、`insert_question()`関数を置き換える
    #   -> DB書き込みを抑止するため
    if args.dry_run:
        print("( ´_ゝ`) < (dry-run) 実際のDB書き込みは行いません。")

        # 一旦、本家`insert_question()`関数を変数`_real_insert`に退避
        #   -> 必要になったときに元に戻せるようにするために、元の関数の参照を保持
        _real_insert = insert_question

        # `insert_question()`を上書きするための関数
        #   -> DB書き込みを伴わない実装
        def _insert_dry(item) -> bool:
            chapter_number = item["chapter_number"]
            section_number = item["section_number"]
            question_number = item["question_number"]
            print(f"(dry) would insert: Chapter={chapter_number}, Section={section_number}, Question={question_number}")
            return not exists_question(chapter_number, section_number, question_number)
        # `insert_question()`関数を`_insert_dry()`関数で乗っ取る
        insert_question = _insert_dry

    try:
        if args.all or args.initial:
            print("Initial import (chpaters/sections) running...")
            initial_import()
        if args.all or args.questions:
            print("Questions import running...")
            import_questions(reimport=args.questions_reset)
    except Exception as e:
        print(f"Error during import: {e}")
        raise

