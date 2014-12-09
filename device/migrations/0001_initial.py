# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Antenna',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('satellite', models.CharField(max_length=200, verbose_name='Sat\xe9lite')),
                ('lnb_type', models.CharField(help_text='Verificar o tipo de LNBf escrito no cabe\xe7ote da antena', max_length=200, verbose_name='Tipo de LNB', choices=[('normal_c', 'C Normal'), ('multiponto_c', 'C Multiponto'), ('universal_k', 'Ku Universal')])),
            ],
            options={
                'verbose_name': 'Antena parab\xf3lica',
                'verbose_name_plural': 'Antenas parab\xf3licas',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeviceServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.BooleanField(default=False, verbose_name='Status', editable=False)),
                ('pid', models.PositiveSmallIntegerField(verbose_name='PID', null=True, editable=False, blank=True)),
                ('description', models.CharField(max_length=250, verbose_name='Descri\xe7\xe3o', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DemuxedService',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('sid', models.PositiveIntegerField(verbose_name='Programa')),
                ('provider', models.CharField(max_length=2000, null=True, verbose_name='Provedor', blank=True)),
                ('service_desc', models.CharField(max_length=2000, null=True, verbose_name='Servi\xe7o', blank=True)),
                ('enabled', models.BooleanField(default=False)),
                ('object_id', models.PositiveIntegerField(null=True)),
            ],
            options={
                'verbose_name': 'Entrada demultiplexada',
                'verbose_name_plural': 'Entradas demultiplexadas',
            },
            bases=('device.deviceserver',),
        ),
        migrations.CreateModel(
            name='DigitalTunerHardware',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_vendor', models.CharField(max_length=100)),
                ('id_product', models.CharField(max_length=100)),
                ('bus', models.CharField(max_length=100)),
                ('driver', models.CharField(max_length=100)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('uniqueid', models.CharField(max_length=100, unique=True, null=True)),
                ('adapter_nr', models.PositiveSmallIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DvbTuner',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('frequency', models.PositiveIntegerField(help_text='MHz', verbose_name='Frequ\xeancia')),
                ('symbol_rate', models.PositiveIntegerField(help_text='Msym/s', verbose_name='Taxa de s\xedmbolos')),
                ('modulation', models.CharField(max_length=200, verbose_name='Modula\xe7\xe3o', choices=[('QPSK', 'QPSK'), ('8PSK', '8-PSK')])),
                ('polarization', models.CharField(max_length=200, verbose_name='Polariza\xe7\xe3o', choices=[('H', 'Horizontal (H)'), ('V', 'Vertical (V)'), ('R', 'Direita (R)'), ('L', 'Esquerda (L)'), ('U', 'N\xe3o especificada')])),
                ('fec', models.CharField(default='999', max_length=200, verbose_name='FEC', choices=[('0', 'Off'), ('12', '1/2'), ('23', '2/3'), ('34', '3/4'), ('35', '3/5'), ('56', '5/6'), ('78', '7/8'), ('89', '8/9'), ('910', '9/10'), ('999', 'Auto')])),
                ('adapter', models.CharField(max_length=200, null=True, verbose_name='Adaptador', blank=True)),
            ],
            options={
                'verbose_name': 'Sintonizador DVB-S/S2',
                'verbose_name_plural': 'Sintonizadores DVB-S/S2',
            },
            bases=('device.deviceserver', models.Model),
        ),
        migrations.CreateModel(
            name='FileInput',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('filename', models.CharField(max_length=255, null=True, verbose_name='Arquivo de origem', blank=True)),
                ('repeat', models.BooleanField(default=True, verbose_name='Repetir indefinidamente')),
            ],
            options={
                'verbose_name': 'Arquivo de entrada',
                'verbose_name_plural': 'Arquivos de entrada',
            },
            bases=('device.deviceserver',),
        ),
        migrations.CreateModel(
            name='IsdbTuner',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('frequency', models.PositiveIntegerField(help_text='MHz', verbose_name='Frequ\xeancia')),
                ('modulation', models.CharField(default='qam', max_length=200, verbose_name='Modula\xe7\xe3o', choices=[('qam', 'QAM')])),
                ('bandwidth', models.PositiveSmallIntegerField(default=6, help_text='MHz', null=True, verbose_name='Largura de banda')),
                ('adapter', models.PositiveSmallIntegerField(null=True)),
            ],
            options={
                'verbose_name': 'Sintonizador ISDB-Tb',
                'verbose_name_plural': 'Sintonizadores ISDB-Tb',
            },
            bases=('device.deviceserver', models.Model),
        ),
        migrations.CreateModel(
            name='MulticastInput',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('port', models.PositiveSmallIntegerField(default=10000, verbose_name='Porta')),
                ('protocol', models.CharField(default='udp', max_length=20, verbose_name='Protocolo de transporte', choices=[('udp', 'UDP'), ('rtp', 'RTP')])),
                ('ip', models.IPAddressField(verbose_name='Endere\xe7o IP multicast')),
            ],
            options={
                'verbose_name': 'Entrada IP multicast',
                'verbose_name_plural': 'Entradas IP multicast',
            },
            bases=('device.deviceserver', models.Model),
        ),
        migrations.CreateModel(
            name='MulticastOutput',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('port', models.PositiveSmallIntegerField(default=10000, verbose_name='Porta')),
                ('protocol', models.CharField(default='udp', max_length=20, verbose_name='Protocolo de transporte', choices=[('udp', 'UDP'), ('rtp', 'RTP')])),
                ('ip', models.IPAddressField(unique=True, verbose_name='Endere\xe7o IP multicast')),
            ],
            options={
                'ordering': ('ip',),
                'verbose_name': 'Sa\xedda IP multicast',
                'verbose_name_plural': 'Sa\xeddas IP multicast',
            },
            bases=('device.deviceserver', models.Model),
        ),
        migrations.CreateModel(
            name='NIC',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Interface de rede')),
                ('ipv4', models.IPAddressField(verbose_name='Endere\xe7o ip v4 atual')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RealTimeEncript',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name='Nome')),
                ('host', models.IPAddressField(unique=True, verbose_name='Host', blank=True)),
                ('username', models.CharField(max_length=200, verbose_name='Usu\xe1rio', blank=True)),
                ('password', models.CharField(max_length=200, verbose_name='Senha', blank=True)),
                ('rsakey', models.CharField(help_text='Exemplo: ~/.ssh/id_rsa', max_length=500, verbose_name='Chave RSA', blank=True)),
                ('ssh_port', models.PositiveSmallIntegerField(default=22, null=True, verbose_name='Porta SSH', blank=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\xdaltima modifica\xe7\xe3o')),
                ('status', models.BooleanField(default=False, verbose_name='Status')),
                ('msg', models.TextField(verbose_name='Mensagem de retorno', blank=True)),
                ('offline_mode', models.BooleanField(default=False)),
                ('server_type', models.CharField(max_length=100, verbose_name='Tipo de Servidor', choices=[('local', 'Servidor local DEMO'), ('dvb', 'Sintonizador DVB'), ('recording', 'Servidor TVoD'), ('nbridge', 'Servidor NBridge')])),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Servidor de Recursos',
                'verbose_name_plural': 'Servidores de Recursos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SoftTranscoder',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('transcode_audio', models.BooleanField(default=False, verbose_name='Transcodificar \xe1udio')),
                ('audio_codec', models.CharField(blank=True, max_length=100, null=True, verbose_name='\xc1udio codec', choices=[('mp2', 'MP2'), ('aac', 'AAC'), ('ac3', 'AC3')])),
                ('apply_gain', models.BooleanField(default=False, verbose_name='Aplicar ganho')),
                ('gain_value', models.FloatField(default=1.0, help_text='Increase or decrease the gain (default 1.0)', null=True, verbose_name='Ganho multiplicador', blank=True)),
                ('apply_offset', models.BooleanField(default=False, verbose_name='Aplicar offset')),
                ('offset_value', models.IntegerField(default=0, help_text='Increase or decrease offset (default 0)', null=True, verbose_name='Valor offset', blank=True)),
            ],
            options={
                'verbose_name': 'Transcodificador em Software',
                'verbose_name_plural': 'Transcodificadores em Software',
            },
            bases=('device.deviceserver',),
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('folder', models.CharField(default=b'/var/lib/iptv/recorder', max_length=500, verbose_name='Diret\xf3rio destino')),
                ('hdd_ssd', models.BooleanField(default=False, verbose_name='Disco SSD (Disco Estado S\xf3lido)')),
                ('peso', models.PositiveIntegerField(default=100, help_text='Prioridade de acesso nas grava\xe7\xf5es', verbose_name='Peso')),
                ('limit_rec_hd', models.PositiveIntegerField(default=0, help_text='N\xfamero m\xe1ximo de grava\xe7\xf5es de fluxo HD', verbose_name='Max. Rec. HD')),
                ('limit_rec_sd', models.PositiveIntegerField(default=0, help_text='N\xfamero m\xe1ximo de grava\xe7\xf5es de fluxo SD', verbose_name='Max. Rec. SD')),
                ('limit_play_hd', models.PositiveIntegerField(default=0, help_text='N\xfamero m\xe1ximo de clientes de fluxo HD', verbose_name='Max. Cli. HD')),
                ('limit_play_sd', models.PositiveIntegerField(default=0, help_text='N\xfamero m\xe1ximo de clientes de fluxo SD', verbose_name='Max. Cli. SD')),
                ('n_recorders', models.PositiveIntegerField(default=0, verbose_name='Grava\xe7\xf5es')),
                ('n_players', models.PositiveIntegerField(default=0, verbose_name='Players')),
            ],
            options={
            },
            bases=('device.deviceserver',),
        ),
        migrations.CreateModel(
            name='StreamPlayer',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('stb_ip', models.IPAddressField(unique=True, verbose_name='IP destino', db_index=True)),
                ('stb_port', models.PositiveSmallIntegerField(default=12000, help_text='Padr\xe3o: 12000', verbose_name='Porta destino')),
                ('control_socket', models.CharField(max_length=500, verbose_name='Socket de controle (auto)')),
                ('time_shift', models.PositiveIntegerField(default=0, verbose_name='Segundos')),
            ],
            options={
                'verbose_name': 'Reprodutor de fluxo gravado',
                'verbose_name_plural': 'Reprodutores de fluxo gravado',
            },
            bases=('device.deviceserver', models.Model),
        ),
        migrations.CreateModel(
            name='StreamRecorder',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('rotate', models.PositiveIntegerField(default=60, help_text='Padr\xe3o \xe9 60 min.', verbose_name='Tempo em minutos do arquivo')),
                ('keep_time', models.PositiveIntegerField(default=48, help_text='Padr\xe3o: 48', verbose_name='Horas que permanece gravado')),
                ('start_time', models.DateTimeField(default=None, null=True, verbose_name='Hora inicial da grava\xe7\xe3o', blank=True)),
                ('stream_hd', models.BooleanField(default=False, help_text='Marcar se o fluxo do canal for HD', verbose_name='Fluxo \xe9 HD')),
            ],
            options={
                'verbose_name': 'Gravador de fluxo',
                'verbose_name_plural': 'Gravadores de fluxo',
            },
            bases=('device.deviceserver', models.Model),
        ),
        migrations.CreateModel(
            name='UnicastInput',
            fields=[
                ('deviceserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='device.DeviceServer')),
                ('port', models.PositiveSmallIntegerField(default=10000, verbose_name='Porta')),
                ('protocol', models.CharField(default='udp', max_length=20, verbose_name='Protocolo de transporte', choices=[('udp', 'UDP'), ('rtp', 'RTP')])),
                ('interface', models.ForeignKey(verbose_name='Interface de rede', to='device.NIC')),
            ],
            options={
                'verbose_name': 'Entrada IP unicast',
                'verbose_name_plural': 'Entradas IP unicast',
            },
            bases=('device.deviceserver', models.Model),
        ),
        migrations.CreateModel(
            name='UniqueIP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.IPAddressField(unique=True, null=True, verbose_name='Endere\xe7o IP')),
                ('port', models.PositiveSmallIntegerField(default=10000, verbose_name='Porta')),
                ('sequential', models.PositiveSmallIntegerField(default=2, verbose_name='Valor auxiliar para gerar o IP \xfanico')),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('ip',),
                'verbose_name': 'Endere\xe7o IPv4 multicast',
                'verbose_name_plural': 'Endere\xe7os IPv4 multicast',
            },
            bases=(models.Model,),
        ),
    ]
