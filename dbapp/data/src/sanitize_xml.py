import xml.etree.ElementTree as ET

def flatten_question_sql(node):
    """質問文 → SQL の階層を平坦化する"""
    new_children = []

    for child in list(node):
        # 子ノードの子に「※」があるか？
        if len(child) == 1 and child[0].attrib.get("text") == "※":
            sql_node = child[0]

            # 質問文ノード（子）をコピーして、SQL ノードとは兄弟にする
            question_node = ET.Element("outline", child.attrib)

            # SQL ノードをコピー
            new_sql_node = ET.Element("outline", sql_node.attrib)

            new_children.append(question_node)
            new_children.append(new_sql_node)
        else:
            new_children.append(child)
            flatten_question_sql(child)

    # すべて置き換え
    node[:] = new_children


def convert_opml(input_path, output_path):
    tree = ET.parse(input_path)
    root = tree.getroot()

    flatten_question_sql(root)

    tree.write(output_path, encoding="utf-8", xml_declaration=True)


# Usage: 
#   convert_opml("input.opml", "output.opml")
convert_opml("dynalist-2025-11-22.opml", "sanitized.opml")
print("done!!")