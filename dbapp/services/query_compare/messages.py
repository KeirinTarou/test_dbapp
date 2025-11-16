from enum import Enum, auto

class CompareResult(Enum):
    OK = auto()
    COLUMN_COUNT_MISMATCH = auto()
    COLUMN_NAME_MISMATCH = auto()
    ROW_COUNT_MISMATCH = auto()
    ROW_ORDER_MISMATCH = auto()
    ROW_CONTENT_MISMATCH = auto()
    OTHER_DEFFERENCE = auto()

    USER_HAS_EXTRA_ROWS = auto()
    USER_MISSING_ROWS = auto()

COMPARE_RESULT_MESSAGES = {
    CompareResult.OK: "🎉🎉🎉お見事！🎉🎉🎉",
    CompareResult.COLUMN_COUNT_MISMATCH: "列数が異なっています。",
    CompareResult.COLUMN_NAME_MISMATCH: "列名が異なっています。",
    CompareResult.ROW_COUNT_MISMATCH: "行数が異なっています。",
    CompareResult.ROW_ORDER_MISMATCH: "行の順序が異なっています。",
    CompareResult.ROW_CONTENT_MISMATCH: "結果セットの内容が一致しません。",
    CompareResult.OTHER_DIFFERENCE: "結果が一致しません。",
    CompareResult.USER_HAS_EXTRA_ROWS: "ユーザクエリに余分な行があります。",
    CompareResult.USER_MISSING_ROWS: "正解に存在する行がユーザクエリの結果にありません。",
}