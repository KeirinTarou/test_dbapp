"use strict";

{

    $(function() {

        /* --------------------------------------------------------------------
            ページ読み込み時の処理
        -------------------------------------------------------------------- */
            // ローカルストレージにテーブル構造のデータがあれば、
            // テーブル構造表示領域を描画する
            $(document).ready(function() {
                // 最後に見たテーブルのテーブル名を取得
                const lastViewed = localStorage.getItem("lastViewedTable");
                // キャッシュデータがあれば、データを取得して描画
                if (lastViewed) {
                    const cacheKey = `table:${lastViewed}`;
                    const cachedData = localStorage.getItem(cacheKey);
                    if (cachedData) {
                        const data = JSON.parse(cachedData);
                        $("#table-structure-wrapper").show();
                        $("#table-structure-title").text(`${lastViewed} テーブルの構造（キャッシュ）`);
                        renderTableStructureTable(data);
                    }
                }
            });

        /* --------------------------------------------------------------------
            ローカルストレージのテーブル構造情報のキャッシュをクリアする
        -------------------------------------------------------------------- */
            $("#cache-clear-icon").on("click", function() {
                // ローカルストレージのテーブル情報キャッシュを削除
                // 表示中のテーブル名を格納するKeyのデータを削除
                localStorage.removeItem('lastViewedTable');

                // `table:`で始まるKeyのデータ（＝キャッシュ済みテーブルのデータ）削除
                Object.keys(localStorage).forEach(key => {
                    if (key.startsWith('table:')) {
                        localStorage.removeItem(key);
                    }
                });

                // テーブル情報表示テーブルをクリア
                $("#table-structure thead, #table-structure tbody").empty();
                // テーブル情報表示領域をdisplay:none;にする。
                $("#table-structure-wrapper").hide();

                // トースト通知
                const notice = $('<div class="toast">🗑️キャッシュを削除しました</div>')
                    .appendTo('body')
                    .hide()
                    .fadeIn(200);
                
                setTimeout(() => {
                    notice.fadeOut(400, function() {
                        $(this).remove();
                    });
                }, 2000);
            });

        /* --------------------------------------------------------------------
            テーブル詳細表示関係
        -------------------------------------------------------------------- */
            $(".pill-list").on("click", ".pill", function(){
                // クリックしたピルケースのdata属性からテーブル名を取得
                const tableName = $(this).data("table");
                // キャッシュのキーを作成
                const cacheKey = `table:${tableName}`;
                // localStorageにキャッシュされたデータを取得
                const cachedData = localStorage.getItem(cacheKey);

                // 最後に見たテーブルのテーブル名をローカルストレージにキャッシュ
                localStorage.setItem("lastViewedTable", tableName);

                // デフォルト非表示の結果表示divを表示
                $("#table-structure-wrapper").show();

                // キャッシュがある場合は即描画
                if (cachedData) {
                    const data = JSON.parse(cachedData);
                    $("#table-structure-title").text(`${tableName} テーブルの構造（キャッシュ）`);
                    // theadとtbodyに闘魂注入
                    renderTableStructureTable(data);
                    // API呼び出しをスキップ
                    return;
                } 

                // キャッシュがないときはAPIを叩く
                // URL組み立て
                const url = `/api/table/${tableName}`;

                // ローディング表示
                $("#table-structure-title").text(`${tableName} テーブル構造を取得中...`);

                // 非同期でWeb APIからJSONを取得
                // 取得するJSON（`data`）の形式は次の通り
                // {
                //      columns: <array of column names>, 
                //      rows: <array of value arrays>, 
                // }
                $.getJSON(url)
                    // 取得成功
                    .done(function(data) {
                        // 通信はできたがエラー
                        if (data.error) {
                            $("#table-structure-title").text("( ´,_ゝ`) < エラー");
                            $("#table-structure thead, #table-structure tbody").empty();
                            $("#table-structure tbody").append(
                                `<tr><td colspan="99">${data.error}</td></tr>`
                            );
                            return
                        }
                        // 正しいデータが返ってきた
                        // ローカルストレージにデータをキャッシュ
                        try {
                            localStorage.setItem(cacheKey, JSON.stringify(data));
                            console.log(`キャッシュ保存: ${cacheKey}`);
                        } catch (e) {
                            console.warn("localStorageへの保存に失敗しました。: ", e);
                        }

                        $("#table-structure-title").text(`${tableName} テーブルの構造`);
                        // theadとtbodyに闘魂注入
                        renderTableStructureTable(data);
                    })
                    // 取得失敗
                    .fail(function() {
                        $("#table-structure-title").text("通信エラー");
                        $("#table-structure thead, #table-structure tbody").empty();
                    }
                );
            });

            // テーブル構造表示テーブル描画用関数
            function renderTableStructureTable(data) {
                const thead = data.columns.map(col => `<th>${col}</th>`).join("");
                $("#table-structure thead").html(`<tr>${thead}</tr>`);

                const rows = data.rows.map(row => 
                    `<tr>${row.map(cell => `<td>${cell}</td>`).join("")}</tr>`).join("");
                $("#table-structure tbody").html(rows);
            }

        /* --------------------------------------------------------------------
            CodeMirror関係
        -------------------------------------------------------------------- */
            // textareaをCodeMirrorに置き換え
            const editor = 
                CodeMirror.fromTextArea(
                    // 置き換えるHTML要素
                    document.getElementById('sql_query'), 
                    // CodeMirrorの設定
                    {
                        mode: 'text/x-sql', 
                        theme: 'eclipse', 
                        lineNumbers: true, 
                        indentWithTabs: true, 
                        smartIndent: true, 
                        autofocus: true, 
                        tabSize: 4, 
                        indentUnit: 4, 
                        placeholder: "( ´_ゝ`) < SELECT文を入力してください。", 
                        extraKeys: {
                            "Tab": function(cm) {
                                if (cm.somethingSelected()) {
                                    cm.indentSelection("add");
                                } else {
                                    cm.replaceSelection("\t");
                                }
                            }, 
                            "Shift-Tab": function(cm) {
                                cm.indentSelection("subtract");
                            }
                        }
                    }
                );

            // CodeMirrorラッパーのdata属性から受け取った値をCodeMirrorオブジェクトにセット
            const height = $('#sql_query_wrapper').data('sql-query-height')
            if (height) {
                editor.setSize("100%", parseInt(height) + "px");
            }

            // フォームサブミット時にCodeMirrorラッパーの高さをinput:hiddenに入れる
            $('form').on('submit', function() {
                const height = $('#sql_query_wrapper').outerHeight();
                $('#sql_query_height').val(height);
            });

            // フォームサブミット時にCodeMirrorの値をtextareaに反映
            $('form').on('submit', function() {
                editor.save(); // textareaの値にコピー
            });

            $("#sql_query_wrapper").resizable({
                handles: "s", // 下側だけリサイズ可
                minHeight: 200, 
                maxHeight: 600, 
                resize: function(event, ui) {
                    // CodeMirrorの高さをラッパーdivに合わせる
                    editor.setSize(null, ui.size.height);
                }
            });

            // クエリコピー機能 & トースト通知
            $('#copy-query-btn').on('click', async function() {
                try {
                    // エディタの値を取得
                    const text = editor.getValue();
                    // クリップボードに書き込み
                    await navigator.clipboard.writeText(text);

                    // トースト通知作成
                    // トースト通知用divを作成・追加
                    const toast = $('<div class="toast">Copied!!</div>');
                    $('body').append(toast);
                    // 2秒後に除去
                    setTimeout(() => toast.remove(), 2000);
                } catch (e) {
                    console.error('コピー失敗: ', e);
                    const toast= $('<div class="toast" style="background:#a00">Copy failed...</div>');
                    $('body').append(toast);
                    setTimeout(() => toast.remove(), 2000);
                }
            });
        
        /* --------------------------------------------------------------------
            スクロール関係
        -------------------------------------------------------------------- */
            const $scrollTarget = $('section[data-scroll="true"]');
            if ($scrollTarget.length) {
                $('html, body').animate(
                    {
                        scrollTop: $scrollTarget.offset().top
                    }, 
                    600, 
                    'swing' 
                );
            }

    });

}