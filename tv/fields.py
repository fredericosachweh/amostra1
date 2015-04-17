#-*- coding: utf-8 -*-
'''
Campos (fields) customizados
'''

from django import forms
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils.encoding import smart_unicode
import os

__all__ = 'DinamicChoiceField', 'ImageField2Wizard',


class DinamicChoiceField(forms.ChoiceField):
    '''
    Campo ChoiceField dinâmico, alimentado por Ajax.
    A validacao deve apenas verificar se o campo esta vazio, nao deve
    verificar se o valor esta no 'choices'.
    '''
    def clean(self, value):
        if bool(value) is False or value == '0':
            raise forms.ValidationError(u'Escolha uma opção válida.')
        return smart_unicode(value)


class DinamicChoiceFieldDemux(forms.ChoiceField):
    '''
    Campo ChoiceField dinâmico, alimentado por Ajax.
    A validacao deve apenas verificar se o campo esta vazio, nao deve
    verificar se o valor esta no 'choices'.
    '''
    def clean(self, value):
        if bool(value) is False or value == '0':
            if value != '-1':
                raise forms.ValidationError(u'Escolha uma opção válida.')
        return smart_unicode(value)


class ImageField2Wizard(forms.ImageField):
    '''
    Campo ImageField para o Wizard
    A validação deve verificar se o arquivo de upload está no diretório,
    buscando através de Session o nome do arquivo.
    '''
    def clean(self, data, initial=None):
        sessions = Session.objects.all()
        used_session = None
        for session in sessions:
            decoded_session = session.get_decoded()
            if 'file_name' in decoded_session.keys():
                file_dir = str(decoded_session['file_name'])
                file_dir = os.path.join(settings.MEDIA_ROOT, file_dir)
                file_name = str(decoded_session['file_name'])
                if os.path.exists(file_dir) and file_name != '':
                    used_session = session
                    break
        if used_session is None:
            raise forms.ValidationError(self.error_messages['empty'])
