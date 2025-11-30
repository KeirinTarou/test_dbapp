"use strict";

{

    $(function() {

        /* --------------------------------------------------------------------
            ページ読み込み時の処理
        -------------------------------------------------------------------- */
            // Flashメッセージのフェイドアウト
            $('.flash').each(function() {
                const $msg = $(this);

                setTimeout(() => {
                    $msg.addClass('fadeout');
                    setTimeout(() => {
                        $msg.remove();    
                    }, 1500);
                }, 2000);
            });

            // ローカルストレージにテーブル構造のデータがあれば、
            // テーブル構造表示領域を描画する
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

            // 煽り画像ズーム
            const logo = $('#loading-logo');
            // アニメーション開始
            logo.addClass('show');
            // アニメーション完了後にDOMから除去
            setTimeout(() => {
                logo.remove();
            }, 1500);

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
            $(".pill-list").on("click", ".pill", function() {
                // 一旦`show`クラスをはがす
                const $container = $('#table-structure-container');
                if ($container.hasClass('show')) {
                    $container.removeClass('show')
                }
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
                const $container = $("#table-structure-container");
                $container.removeClass('show');

                setTimeout(() => {
                    const thead = data.columns.map(col => `<th>${col}</th>`).join("");
                    $("#table-structure thead").html(`<tr>${thead}</tr>`);

                    const rows = data.rows.map(row => 
                        `<tr>${row.map(cell => `<td>${cell}</td>`).join("")}</tr>`).join("");
                    $("#table-structure tbody").html(rows);

                    $container.addClass('show');
                }, 20);
            }

        /* --------------------------------------------------------------------
            CodeMirror関係
        -------------------------------------------------------------------- */
            // textareaをCodeMirrorに置き換え
            const textarea = document.getElementById('sql_query');
            let sqlEditor
            if (textarea) {
                sqlEditor = 
                    CodeMirror.fromTextArea(
                        // 置き換えるHTML要素
                        textarea, 
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
            }

            // CodeMirrorラッパーのdata属性から受け取った値をCodeMirrorオブジェクトにセット
            const $queryWrapper = $('#sql_query_wrapper');
            const height = $queryWrapper.data('sql-query-height')
            if (sqlEditor && height) {
                sqlEditor.setSize("100%", parseInt(height) + "px");
            }

            // フォームサブミット時にCodeMirrorラッパーの高さをinput:hiddenに入れる
            //      -> CodeMirrorの値をtextareaに反映
            $('#form--submit-query').on('submit', function() {
                const height = $queryWrapper.outerHeight();
                $('#sql_query_height').val(height);
                if (sqlEditor) sqlEditor.save(); // textareaの値にコピー
            });

            $queryWrapper?.resizable({
                handles: "s", // 下側だけリサイズ可
                minHeight: 200, 
                maxHeight: 600, 
                resize: function(event, ui) {
                    // CodeMirrorの高さをラッパーdivに合わせる
                    sqlEditor.setSize(null, ui.size.height + "px");
                }
            });

            // クリアボタン押下で
            $("#clear-query-btn").on("click", function() {
                const val = sqlEditor.getValue()
                let msg = "";
                if (val === "") {
                    msg = "( ´,_ゝ`) < 何も書いてへんがなｗｗｗ"
                } else if (confirm("( ´_ゝ`) < 入力したクエリをクリアします。")) {
                    // CodeMirrorのテキストをクリア
                    sqlEditor.setValue("");
                    // 元のtextareaのテキストもクリア
                    $("#sql_query").val("");
                    msg = "( ´,_ゝ`) < クリアしましたｗ";
                } else {
                    msg = "( ´,_ゝ`) < クリアせんのかいｗｗｗ";
                }
                // トースト通知
                    const toast = $(`<div class="toast">${msg}</div>`);
                    $('body').append(toast);
                    // 2秒後に除去
                    setTimeout(() => toast.remove(), 2000);
            });

            // クエリコピー機能 & トースト通知
            $('#copy-query-btn').on('click', async function() {
                try {
                    // エディタの値を取得
                    const text = sqlEditor.getValue();
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

            // 問題データ編集用のエディタ
            const answerEditorEl = document.getElementById('answer_edit')
            if (answerEditorEl) {
                const answerEditor = CodeMirror.fromTextArea(answerEditorEl, {
                    mode: 'text/x-sql', 
                    theme: 'eclipse', 
                    lineNumbers: true, 
                    tabSize: 4, 
                    indentUnit: 4, 
                    indentWithTabs: true, 
                    smartIndent: true, 
                    autofocus: true, 
                    placeholder:"( ´,_ゝ`) < なんで空白やねんｗｗｗ", 
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
                });

                $('#form--edit-question').on('submit', function() {
                    answerEditor.save(); // textareaの値にコピー
                });
            }
        
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

        /* --------------------------------------------------------------------
            判定結果表示ページのトグルテーブル
        -------------------------------------------------------------------- */
        $('.heading.toggle-header').on('click', function() {
            const content = $(this).next('.toggle-content');
            const isClosed = content.hasClass('is-close');

            if (isClosed) {
                $(this).removeClass('is-close').addClass('is-open');
                $(this).attr('title', '( ´_ゝ`) < クリックで表示を折りたたみます。')
                
                // テーブル部分のis-close/is-openの切り替えを少し遅らせる
                setTimeout(() => {
                    content.removeClass('is-close').addClass('is-open');
                }, 200);
                
                content.one('transitionend', function() {
                    const maxHeight = parseInt(content.css('max-height'));
                    // 実際の高さを取得
                    const actualHeight = content.prop('scrollHeight');
                    // 実際のスクロール量
                    const scrollAmount = Math.min(maxHeight, actualHeight);
                    // なめらかスクロール
                    $('html, body').animate(
                        { scrollTop: $(window).scrollTop() + scrollAmount }, 
                        400
                    );
                });

            } else {
                $(this).removeClass('is-open').addClass('is-close')
                $(this).attr('title', '( ´,_ゝ`) < クリックで表示を展開します。')
                setTimeout(() => {
                    content.removeClass('is-open').addClass('is-close')
                }, 200); 
            }
        });

    });

}