# -*- encoding:utf-8 -*-
from device.models import UniqueIP, StreamRecorder, FileInput
from device.models import SoftTranscoder
from django.contrib.admin.helpers import AdminForm
from django.contrib.formtools.wizard import FormWizard
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from models import Channel
from tv.forms import InputChooseForm, ChannelForm
from tv.forms import StreamRecorderForm, AudioConfigsForm
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from device.models import DemuxedService

import os


class ChannelCreationWizard(FormWizard):
    "Formulários de criação do canal"

    @property
    def __name__(self):
        return self.__class__.__name__

    def get_dir_to_save_image(self):
        return 'tv/channel/image/original/'

    def get_dir_to_save_thumb(self):
        return 'tv/channel/image/thumb/'

    def insert_optional_form(self, form, next_form_step, model_form):
        if not model_form in self.form_list:
            self.form_list.insert(next_form_step, model_form)
            next_form_step = next_form_step + 1
        return next_form_step

    def remove_optional_form(self, model_form):
        if model_form in self.form_list:
            self.form_list.remove(model_form)

    def clean_request_session(self, request):
        request.session['file_name'] = ''
        request.session.save()

    def process_step(self, request, form, step):
        next_form_step = 2
        if step == 1:
            if form.cleaned_data.get('audio_config'):
                next_form_step = self.insert_optional_form(form,
next_form_step, AudioConfigsForm)
            else:
                self.remove_optional_form(AudioConfigsForm)
            if form.cleaned_data.get('gravar_config'):
                next_form_step = self.insert_optional_form(form,
next_form_step, StreamRecorderForm)
            else:
                self.remove_optional_form(StreamRecorderForm)

    def copy_file(self, request, logo_name, channel_id_as_name):
        '''
        Copy the file selected with ImageField and create the thumb
        '''
        # Caso não exista, cria o diretório
        MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
        if os.path.exists(os.path.join(MEDIA_ROOT,
'tv/channel/image/thumb')) == False:
            os.mkdir(os.path.join(MEDIA_ROOT, 'tv/channel/image/thumb'))
        if os.path.exists(os.path.join(MEDIA_ROOT,
'tv/channel/image/original')) == False:
            os.mkdir(os.path.join(MEDIA_ROOT, 'tv/channel/image/original'))

        image = request.FILES[logo_name]
        image_url = self.get_dir_to_save_image() + channel_id_as_name
        default_storage.save(image_url, ContentFile(image.read()))
        # Thumb
        try:
            import Image
        except ImportError:
            from PIL import Image
        MEDIA_ROOT = '%s/' % (getattr(settings, 'MEDIA_ROOT'))
        thumb_dir = self.get_dir_to_save_thumb()
        image_absolute_url = MEDIA_ROOT + image_url
        thumb_url = '%s%s%s' % (MEDIA_ROOT, thumb_dir, channel_id_as_name)
        thumb = Image.open(image_absolute_url)
        thumb.thumbnail((200, 200), Image.ANTIALIAS)
        thumb.save(thumb_url)

    def get_form_title(self, step, request):
        title = {None: 'Entrada de Fluxo',
                 '0': 'Adicionar Canal',
                 '1': 'Configurar Audio',
                 '2': 'Configurar Gravação',
                 '3': None}
        return title[step]

    def parse_params(self, request, admin=None, *args, **kwargs):
        '''
        Save into request.session the key 'file_name',
        that contains the local where the image was saved.
        '''
        if request.FILES:
            logo_name = '1-image'
            file_name = str(request.FILES[logo_name])
            extension = file_name.split('.')[-1]
            channel_id_key = '1-number'
            channel_id_value = request.POST[channel_id_key]
            channel_id_as_name = '%s.%s' % (channel_id_value, extension)
            request.session['file_name'] = '%s%s.%s' % (
self.get_dir_to_save_image(), channel_id_value, extension)
            request.session.save()
            self.copy_file(request, logo_name, channel_id_as_name)

        self._model_admin = admin
        opts = admin.model._meta
        step = request.POST.get('wizard_step')
        title = self.get_form_title(step, request)
        self.extra_context.update({
            'title': title,
            'current_app': admin.admin_site.name,
            'has_change_permission': admin.has_change_permission(request),
            'add': True,
            'opts': opts,
            'app_label': 'opts.app_label',
            'step': step
        })
        return super(ChannelCreationWizard, self).parse_params(request, admin)

    def render_template(self, request, form, previous_fields, step, \
context=None, step_title=None):
        '''
        Renders the template for the given step,
        returning an HttpResponse object.
        '''
        if step == 0:
            self.clean_request_session(request)
            if AudioConfigsForm in self.form_list:
                self.remove_optional_form(AudioConfigsForm)
            if StreamRecorderForm in self.form_list:
                self.remove_optional_form(StreamRecorderForm)

        fieldsets = []
        if form.__class__ == AudioConfigsForm:
            fieldsets = form.fieldsets.__dict__['fieldsets']
        else:
            fieldsets = [('Passo %d de %d' % (step + 1, self.num_steps()),
{'fields': form.base_fields.keys()})]
        form = AdminForm(form, fieldsets, {})
        context = context or {}
        context.update({
            'media': self._model_admin.media + form.media
        })
        return super(ChannelCreationWizard, self).render_template(request,
form, previous_fields, step, context)

    def get_uniqueIP_to_save(self, sequential):
        ip_uniqueIp = settings.EXTERNAL_IP_MASK % (sequential / 256,
sequential % 256)
        return ip_uniqueIp

    def done(self, request, form_list):
        '''
        Final step, save into dabases
        '''
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)

        sink_unique = None
        source_id_name = '1-source'
        if data['demuxed_input'] and (data['demuxed_input'] != '-1'):
            sink_unique = DemuxedService.objects.get(id=data['demuxed_input'])
        else:
            sink_unique = FileInput.objects.get(id=data['input_stream'])
        uniqueIp = UniqueIP.create(sink_unique)
        sequential = uniqueIp.sequential
        sequential = sequential + 1
        ip_uniqueIp = self.get_uniqueIP_to_save(sequential)
        uniqueIp.ip = ip_uniqueIp
        uniqueIp.save()

        '''
        Atualiza object_id da saída multicast
        '''
        data['source'].object_id = uniqueIp.pk
        # Endereço IPv4 multicast
        # TODO: Review
        data['source'].content_type = ContentType.objects.get(id=20)
        data['source'].save()
        logo = request.session['file_name']
        thumb = logo
        # Create channel's values
        channel = Channel.objects.create(
           number=data['number'],
           name=data['name'],
           image=logo,
           thumb=thumb,
           source_id=request.POST[source_id_name],
           channelid=data['channelid'],
           enabled=data['enabled'],
        )

        if 'audio_codec' in data.keys():
            # Create AudioConfig if filled
            SoftTranscoder.objects.create(
                nic_sink=data['nic_sink'],
                nic_src=data['nic_src'],
                content_type=data['content_type'],
                object_id=data['object_id'],
                sink=data['nic_sink'],
                server=data['server'],
                # Audio transcoder
                transcode_audio=data['transcode_audio'],
                audio_codec=data['audio_codec'],
                audio_bitrate=data['audio_bitrate'],
                sync_on_audio_track=data['sync_on_audio_track'],
                # Gain control filter
                apply_gain=data['apply_gain'],
                gain_value=data['gain_value'],
                # Dynamic range compressor
                apply_compressor=data['apply_compressor'],
                compressor_rms_peak=data['compressor_rms_peak'],
                compressor_attack=data['compressor_attack'],
                compressor_release=data['compressor_release'],
                compressor_threshold=data['compressor_threshold'],
                compressor_ratio=data['compressor_ratio'],
                compressor_knee=data['compressor_knee'],
                compressor_makeup_gain=data['compressor_makeup_gain'],
                # Volume normalizer
                apply_normvol=data['apply_normvol'],
                normvol_buf_size=data['normvol_buf_size'],
                normvol_max_level=data['normvol_max_level'],
            )

        if 'keep_time' in data.keys():
            # Create RecorderConfig if filled
            StreamRecorder.objects.create(
                keep_time=data['keep_time'],
                rotate=data['rotate'],
                description=data['description'],
                nic_sink=channel.source.nic_sink,
                object_id=uniqueIp.pk,
                server=data['server'],
                channel=channel,
            )

        self.clean_request_session(request)

        return self._model_admin.response_add(request, channel)


create_canal_wizard = ChannelCreationWizard([InputChooseForm, ChannelForm])
