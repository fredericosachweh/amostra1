from __future__ import unicode_literals
from itertools import chain
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.contenttypes.models import ContentType
import logging
log = logging.getLogger('debug')


class ContentTypeSelect(forms.Select):

    def __init__(self, lookup_id, attrs=None, choices=()):
        self.lookup_id = lookup_id
        super(ContentTypeSelect, self).__init__(attrs, choices)

    def render(self, name, value, attrs=None, choices=()):
        output = super(ContentTypeSelect, self).render(name, value, attrs, choices)
        choices = chain(self.choices, choices)
        choiceoutput = ' var %s_choice_urls = {' % (attrs['id'],)
        # import ipdb
        # ipdb.set_trace()
        for choice in choices:
            try:
                ctype = ContentType.objects.get(pk=int(choice[0]))
                choiceoutput += '    \'%s\' : \'../../../%s/%s?p=%s&_to_field=id\',' % (
                    str(choice[0]),
                    ctype.app_label,
                    ctype.model,
                    ctype.model_class()._meta.pk.name
                )
            except:
                pass
        choiceoutput += '};'
# <a href="/tv/administracao/device/uniqueip/?_to_field=id" class="related-lookup" \
# id="lookup_id_object_id" onclick="return showRelatedObjectLookupPopup(this);"> \
# <img src="/tv/static/admin/img/selector-search.gif" width="16" height="16" alt="Olhar"></a>
# ============================================================================================
# <a href="../../../device/fileinput?t=deviceserver_ptr" class="related-lookup" \
# id="lookup_id_object_id" onclick="return showRelatedObjectLookupPopup(this);"> \
# <img src="/tv/static/admin/img/selector-search.gif" width="16" height="16" alt="Olhar"></a>
        output += ('<script type="text/javascript">\n'
                   '(function($) {\n'
                   '  $(document).ready( function() {\n'
                   '%(choiceoutput)s\n'
                   '    $(\'#%(id)s\').change(function (){\n'
                   '        $(\'#%(fk_id)s\').attr(\'href\',%(id)s_choice_urls[$(this).val()]);\n'
                   '    });\n'
                   '  });\n'
                   '})(django.jQuery);\n'
                   '</script>\n' % {
                       'choiceoutput': choiceoutput,
                       'id': attrs['id'],
                       'fk_id': self.lookup_id
                   })
        return mark_safe(''.join(output))