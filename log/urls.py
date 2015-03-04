from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^current-task-log/$', 'log.views.current_task_log', name='current_task_log'),
)
