# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.dispatch import receiver


class TaskLogManager(models.Manager):
    def create_or_alert(self, name, pks_list, user):
        if not TaskLog.objects.filter(name=name, is_finished=False).exists():
            task = self.create(
                name=name,
                pks_list=list(pks_list),
                user=user,
            )
            return task
        return False


NAME_CHOICES = (
    ('reload-channels', 'Recarregar lista de canais'),
    ('reboot-stbs', 'Reiniciar SetTopBoxes'),
    ('accept-recorder', 'Liberar canais para acessar gravação'),
    ('refuse-recorder', 'Bloquear canais para acessar gravação'),
    ('reload-frontend-stbs', 'Reiniciar frontend dos SetTopBoxes'),
)


class TaskLog(models.Model):
    name = models.CharField(max_length=255, choices=NAME_CHOICES)
    pks_list = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    end_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    is_finished = models.BooleanField(default=False)
    progress = models.DecimalField(default=0.0, decimal_places=2, max_digits=5)
    objects = TaskLogManager()

    def __unicode__(self):
        return self.get_name_display()


@receiver(models.signals.post_save, sender=TaskLog)
def TaskLog_post_save(sender, instance, **kwargs):
    if instance.is_finished:
        cache.delete('task_log-{}'.format(instance.id))