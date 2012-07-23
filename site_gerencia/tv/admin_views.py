# -*- encoding:utf-8 -*-
from device.models import UniqueIP, StreamRecorder
from device.models import SoftTranscoder
from django.contrib.admin.helpers import AdminForm
from django.contrib.formtools.wizard import FormWizard
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from models import Channel
from tv.forms import DemuxedServiceFormWizard, InputChooseForm, ChannelForm
from tv.forms import StreamRecorderForm, AudioConfigsForm
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from device.models import DemuxedService
from django import forms
from django.utils.translation import ugettext as _


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

    def get_next_form_step(self, request):
        next_form_step = 2
        hasDemux = self.has_demux_step(request)
        if hasDemux:
            next_form_step = next_form_step + 1
        return next_form_step

    def remove_optional_form(self, model_form):
        if model_form in self.form_list:
            self.form_list.remove(model_form)

    def clean_request_session(self, request):
        # Remove image name from session
        request.session['file_name'] = ''
        request.session.save()

    def process_step(self, request, form, step):
        # Add DemuxedServiceFormWizard
        if step == 0 and request.POST:
            hasDemux = self.has_demux_step(request)
            if hasDemux:
                if DemuxedServiceFormWizard in self.form_list:
                    self.form_list.remove(DemuxedServiceFormWizard)
                self.form_list.insert(1, DemuxedServiceFormWizard)
            else:
                if DemuxedServiceFormWizard in self.form_list:
                    self.form_list.remove(DemuxedServiceFormWizard)
        # Add optional forms
        next_form_step = self.get_next_form_step(request)
        last_step = next_form_step - 1
        if last_step == step:
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

    def get_logo_name(self, hasDemux):
        logo_name = '1-image'
        if hasDemux:
            logo_name = '2-image'
        return logo_name

    def get_source_id_name(self, hasDemux):
        source_id_name = '1-source'
        if hasDemux:
            source_id_name = '2-source'
        return source_id_name

    def get_channel_id(self, hasDemux):
        channel_id = '1-channelid'
        if hasDemux:
            channel_id = '2-channelid'
        return channel_id

    def get_form_title(self, hasDemux, step, request):
        title = {None: 'Entrada de Fluxo',
                 '0': 'Entrada Demultiplexada',
                 '1': 'Adicionar Canal',
                 '2': 'Configurar Audio',
                 '3': 'Configurar Gravação',
                 '4': None}
        if not hasDemux:
            if step >= 0:
                alter_step = str(int(step) + 1)
                step = alter_step
        if step is not None:
            if ('2-gravar_config' in request.POST or '1-gravar_config' in \
request.POST):
                if not ('2-audio_config' in request.POST or '1-audio_config' \
in request.POST):
                    step = str(int(step) + 1)
        return title[step]

    def has_demux_step(self, request):
        hasDemux = False
        if request.POST:
            input_type = request.POST.get('0-input_types_field')
            hasDemux = input_type == 'dvbs' or input_type == 'isdb' or \
input_type == 'entradas_unicast' or input_type == 'entradas_multicast'
        return hasDemux

    def parse_params(self, request, admin=None, *args, **kwargs):
        '''
        Save into request.session the key 'file_name',
        that contains the local where the image was saved.
        '''
        hasDemux = self.has_demux_step(request)
        if request.FILES:
            logo_name = self.get_logo_name(hasDemux)
            file_name = str(request.FILES[logo_name])
            extension = file_name.split('.')[-1]
            channel_id_key = self.get_channel_id(hasDemux)
            channel_id_value = request.POST[channel_id_key]
            channel_id_as_name = '%s.%s' % (channel_id_value, extension)
            request.session['file_name'] = '%s%s.%s' % (
self.get_dir_to_save_image(), channel_id_value, extension)
            request.session.save()
            self.copy_file(request, logo_name, channel_id_as_name)

        self._model_admin = admin
        opts = admin.model._meta
        step = request.POST.get('wizard_step')
        title = self.get_form_title(hasDemux, step, request)
        self.extra_context.update({
            'title': title,
            'current_app': admin.admin_site.name,
            'has_change_permission': admin.has_change_permission(request),
            'add': True,
            'opts': opts,
            #'root_path': admin.admin_site.root_path,
            'app_label': 'opts.app_label',
            'step': step
        })
        return super(ChannelCreationWizard, self).parse_params(request, admin)

    def get_content_type_id(self, content_type_key):
        ''' Values from device_content_type '''
        content_type = {'dvbs': 26,
                        'isdb': 27,
                        'entradas_unicast': 28,
                        'entradas_multicast': 29}[content_type_key]
        return content_type

    def demuxed_input_field(self):
        objects_ids = []
        for ip in UniqueIP.objects.all():
            objects_ids.append(ip.object_id)
        model = DemuxedService.objects
        for ob_id in objects_ids:
            model = model.exclude(deviceserver_ptr_id=ob_id)
        demuxed_input = forms.ModelChoiceField(model, label=_(u'Entrada'))
        return demuxed_input

    def render_template(self, request, form, previous_fields, step, \
context=None, step_title=None):
        '''
        Renders the template for the given step,
        returning an HttpResponse object.
        '''
        if step == 0:
            self.clean_request_session(request)
        if step == 1:
            form.fields['demuxed_input'] = self.demuxed_input_field()
        # Wrap the form into a AdminForm to get the fieldset
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
        # Verify and set fields to save
        hasDemux = self.has_demux_step(request)
        source_id_name = self.get_source_id_name(hasDemux)
        # Create UniqueIP connector between DemuxServer n' Channel
        sink_unique = data['demuxed_input']
        uniqueIp = UniqueIP.create(sink_unique)
        sequential = uniqueIp.sequential
        # TODO: Review
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
                nic_sink=channel.source.sink.sink.nic_src,
                object_id=channel.source.sink.pk,
                server=data['server'],
                channel=channel,
            )

        self.clean_request_session(request)

        return self._model_admin.response_add(request, channel)


create_canal_wizard = ChannelCreationWizard([InputChooseForm, ChannelForm])
