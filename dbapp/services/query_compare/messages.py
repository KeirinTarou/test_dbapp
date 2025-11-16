from enum import Enum, auto

class CompareResult(Enum):
    OK = auto()
    COLUMN_COUNT_MISMATCH = auto()
    COLUMN_NAME_MISMATCH = auto()
    ROW_COUNT_MISMATCH = auto()
    ROW_ORDER_MISMATCH = auto()
    ROW_CONTENT_MISMATCH = auto()
    OTHER_DIFFERENCE = auto()

    USER_HAS_EXTRA_ROWS = auto()
    USER_MISSING_ROWS = auto()

COMPARE_RESULT_MESSAGES = {
    CompareResult.OK: "🎉🎉🎉お見事！🎉🎉🎉",
    CompareResult.COLUMN_COUNT_MISMATCH: "( ´,_ゝ`) < 列数が異なっています。",
    CompareResult.COLUMN_NAME_MISMATCH: "( ´,_ゝ`) < 列名が異なっています。",
    CompareResult.ROW_COUNT_MISMATCH: "( ´,_ゝ`) < 行数が異なっています。",
    CompareResult.ROW_ORDER_MISMATCH: "( ´,_ゝ`) < 行の順序が異なっています。",
    CompareResult.ROW_CONTENT_MISMATCH: "( ´,_ゝ`) < 結果セットの内容が一致しません。",
    CompareResult.OTHER_DIFFERENCE: "( ´,_ゝ`) < 結果が一致しません。",
    CompareResult.USER_HAS_EXTRA_ROWS: "( ´,_ゝ`) < ユーザークエリに余分な行があります。",
    CompareResult.USER_MISSING_ROWS: "( ´,_ゝ`) < 正解に存在する行がユーザークエリの結果にありません。",
}