"use strict";

{

    $(function() {
        // textareaをCodeMirrorに置き換え
        const editor = 
            CodeMirror.fromTextArea(document.getElementById('sql_query'), {
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
        });

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
    });

}