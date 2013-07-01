# -*- encoding:utf-8 -*-

from optparse import make_option
from django.core.management.base import BaseCommand


class Command(BaseCommand):    
    help = u'Inicia a execução dos aplicativos NodeJS'

    def handle(self, **options):
        from node.models import Node

        print 'Running nodes app'

        apps = Node.objects.all()
        for app in apps:
            app.start()
