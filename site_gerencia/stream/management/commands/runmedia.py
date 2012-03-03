# -*- encoding:utf-8 -*-

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand

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

    def handle(self, **options):
        ## inicia os vlcs
        from device.models import Vlc, Server
        vlcs = Vlc.objects.all()
        for vlc in vlcs:
            if vlc.status == True:
                print('Iniciando:%s' %vlc)
                vlc.start()
        #streams = Stream.objects.filter(pid__isnull=False)
        #for stream in streams:
        #    if options.get('debug') > 0:
        #        self.stdout.write('Iniciando stream [%s]\n' %stream)
        #    stream.autostart()
        #dvbs = DVBSource.objects.filter(pid__isnull=False)
        #for dvb in dvbs:
        #    if options.get('debug') > 0:
        #        self.stdout.write('Iniciando DVB [%s]\n' %dvb)
        #    dvb.autostart()
        

