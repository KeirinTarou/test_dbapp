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

        // フォームサブミット時にCodeMirrorの値をtextareaに反映
        $('form').on('submit', function() {
            editor.save(); // textareaの値にコピー
        });
    });

}