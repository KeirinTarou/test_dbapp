import sqlite3
import os

def init_db():
    """ DBファイル`practice.db`を`schema.sql`によって初期化
    """
    base = os.path.dirname(__file__)
    db_path = os.path.join(base, "practice.db")
    schema_path = os.path.join(base, "schema.sql")

    with open(schema_path, encoding="utf-8") as f:
        schema = f.read()

    with sqlite3.connect(db_path) as conn:
        # 外部キー制約を有効にする
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()
        cur.executescript(schema)
        conn.commit()
    
    print("( ´,_ゝ`) < 'practice.db'を初期化しましたｗｗｗ")

if __name__ == "__main__":
    init_db()