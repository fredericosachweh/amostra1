from django.contrib import admin
from . import models


class TaskLogAdmin(admin.ModelAdmin):
    list_display = ['name', 'progress', 'is_finished']

admin.site.register(models.TaskLog, TaskLogAdmin)

