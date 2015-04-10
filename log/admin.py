from django.apps import apps
from django.contrib import admin


class TaskLogAdmin(admin.ModelAdmin):
    list_display = ['name', 'progress', 'is_finished']

#admin.site.register(apps.get_model('log', 'TaskLog'), TaskLogAdmin)