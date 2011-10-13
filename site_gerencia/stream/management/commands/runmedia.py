# -*- encoding:utf-8 -*-

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand

from stream.models import Stream

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--debug','-d',
            action='store_true',
            dest='debug',
            default=False,
            help='Debug startup stream'),
    )
    help = 'Inicia a execução dos fluxos'
    args = '<media_id media_id ...>'
    #self.can_import_settings = True

    #def handle(self,**options):
    def handle(self, **options):
        print(options.get('debug'))
        streams = Stream.objects.all()
        for stream in streams:
            self.stdout.write('Iniciando canal [%s]\n' %stream)
            stream.play()
        
        self.stdout.write('Terminando handle com sucesso.\n')
        

