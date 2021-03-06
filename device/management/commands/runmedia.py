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

    def handle(self, **options):
        ## inicia os vlcs (Temporário)
        from device.models import FileInput
        files = FileInput.objects.all()
        for fi in files:
            if fi.status == True and fi.running() is False:
                fi.start()
