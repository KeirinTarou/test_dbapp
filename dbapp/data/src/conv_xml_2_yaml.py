import xml.etree.ElementTree as ET
import re
import yaml

def extract_sql(note_text: str) -> str:
    """_note の中の ``` ～ ``` に囲まれた SQL を抽出し整形"""
    # `&#10`は`\n`に変換
    note_text = note_text.replace("&#10;", "\n")

    # 改行直後のスペース2n個 → TAB n個
    def repl(match):
        spaces = match.group(1)
        tabs = "\t" * (len(spaces) // 2)
        return "\n" + tabs
    # `note_text`について、`\n( +)`にマッチする文字列ごとに
    # `repl()`で変換する
    note_text = re.sub(r"\n( +)", repl, note_text)

    # SQL 抽出
    # `re.DOTALL`で`.`改行をまたいでマッチするように指定
    m = re.search(r"```(.*?)```", note_text, re.DOTALL)
    if not m:
        return ""
    # "```(.*?)```"は、3連バッククオートで括られた文字列全体にマッチする
    # 3連クォートで括られた中身が`()`でグループになっているので、
    #   - 3連クォートも含めた全体が`group(0)`
    #   - 3連クォートを除いた中身が`group(1)`
    #   で取り出せる
    sql = m.group(1).strip()

    return sql

def parse_outline(elem, chapter_num=None, section_num=None):
    """outline ノードを再帰的にパースしてリストを返す"""
    results = []

    # 第X章 → chapter 番号
    #   `elem.get("text", "")`で要素の`text`属性を取り出す
    #   text属性がないときは`""`を返す
    #   `chapter_match`には`None`が格納される
    chapter_match = re.match(r"第(\d+)章", elem.get("text", ""))
    # マッチする文字列があったら、数字の部分を取り出す
    if chapter_match:
        chapter_num = int(chapter_match.group(1))

    # 【そのY】 → section 番号
    section_match = re.match(r"【その(\d+)】", elem.get("text", ""))
    if section_match:
        section_num = int(section_match.group(1))
        question_counter = 0

    # 子要素を処理
    # `outline`要素を1つずつ処理
    for child in elem.findall("outline"):
        text = child.get("text", "")

        # 質問は 「第N問」 または 通常テキスト
        if text.startswith("第") and "問" in text:
            # 問単位
            q_elems = child.findall("outline")
            # `outline`要素に子要素が2ついじょうあるとき
            if len(q_elems) >= 2:
                # 1つ目の要素の`text`属性の値が問題
                # 2つ目の要素の`_note`属性の値に正解クエリが含まれる
                q_text = q_elems[0].get("text")
                a_note = q_elems[1].get("_note")
                results.append({
                    "chapter_number": chapter_num,
                    "section_number": section_num,
                    "question_number": question_counter,
                    "question": q_text,
                    "answer_query": extract_sql(a_note), 
                    "check_mode": "strict"
                })
                question_counter += 1

        # 「書いてみよう」などの通常質問セット
        elif text == "書いてみよう":
            q_elems = child.findall("outline")
            if len(q_elems) >= 2:
                q_text = q_elems[0].get("text")
                a_note = q_elems[1].get("_note")
                results.append({
                    "chapter_number": chapter_num,
                    "section_number": section_num,
                    "question_number": question_counter,
                    "question": q_text,
                    "answer_query": extract_sql(a_note), 
                    "check_mode": "strict"
                })
                question_counter += 1

        # 配下のさらに深い outline も走査
        results.extend(parse_outline(child, chapter_num, section_num))

    return results


# --- 実行部分 ---
if __name__ == "__main__":
    # XMLからElementTreeオブジェクトを取得
    tree = ET.parse("sanitized.opml")
    root = tree.getroot()
    body = root.find("body")
    results = []

    for outline in body.findall("outline"):
        results.extend(parse_outline(outline))

    # YAMLとして保存
    with open("output.yaml", "w", encoding="utf-8") as f:
        yaml.dump(results, f, allow_unicode=True, sort_keys=False)

    print("YAML 出力完了")
