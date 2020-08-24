import json

from django import forms
from django.utils.safestring import mark_safe

MEDIA_PREFIX = '/static/custom_dbtemplates'

SCRIPT_HTML = u"""\
<script type="text/javascript">
  var editor = CodeMirror.fromTextArea('id_%(name)s', %(params)s);
</script>
"""


class CodeMirrorTextArea(forms.Textarea):
    """
    A custom widget for the CodeMirror browser editor to be used with the
    content field of the Template model.
    """

    editor_params = {
        'parserfile': 'parsedjango.js',
        'continuousScanning': 500,
        'height': '40.2em',
        'tabMode': 'shift',
        'indentUnit': 4,
        'lineNumbers': False,
    }

    class Media:
        css = {
            'screen': [
                f'{MEDIA_PREFIX}/css/codemirror/editor.css',
            ],
        }
        js = [
            f'{MEDIA_PREFIX}/js/codemirror/codemirror.js',
        ]

    def render(self, name, value, attrs=None, renderer=None):
        params = dict(self.editor_params, **{
            'path': f'{MEDIA_PREFIX}/js/codemirror/',
            'stylesheet': f'{MEDIA_PREFIX}/css/codemirror/django.css',
        })
        context = {
            'name': name,
            'params': json.dumps(params),
        }
        result = [
            super(CodeMirrorTextArea, self).render(name, value, attrs),
            SCRIPT_HTML % context,
        ]
        return mark_safe(u"".join(result))


TemplateContentTextArea = CodeMirrorTextArea
