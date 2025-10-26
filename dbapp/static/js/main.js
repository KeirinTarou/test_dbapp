"use strict";

{

    $(function() {
        /* --------------------------------------------------------------------
            テーブル詳細表示関係
        -------------------------------------------------------------------- */
            $(".pill-list").on("click", ".pill", function(){
                // クリックしたピルケースのdata属性からテーブル名を取得
                const tableName = $(this).data("table");
                // URL組み立て
                const url = `/api/table/${tableName}`;

                // ローディング表示
                $("#table-structure-title").text(`${tableName} テーブル構造を取得中...`);
                // 非表示の結果表示divを表示
                $("#table-structure-container").show();
            });

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