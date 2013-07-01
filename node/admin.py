# -*- coding: utf-8 -*-

from django.contrib import admin
import models


class ApplicationAdmin(admin.ModelAdmin):
	pass


admin.site.register(models.Node)
