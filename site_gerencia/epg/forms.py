#!/usr/bin/env python
# -*- encoding:utf8 -*-

from django import forms
import epg


class Epg_Source_Form(forms.ModelForm):

    class Meta:
        model = epg.models.Epg_Source
        #fields = ('filefield', \
        #    'source_info_url', \
        #    'source_info_name', \
        #    'source_data_url', \
        #    'generator_info_name', \
        #    'generator_info_url', \
        #    'minor_start', \
        #    'major_stop', \
        #    'numberofElements', \
        #    )
