# -*- encoding:utf-8 -*-
from django.contrib.formtools.wizard import FormWizard
from django.utils.encoding import force_unicode

from device.models import *

from forms import *
from models import Canal


class CanalCreationWizard(FormWizard):
    "Formulários de criação do canal"
    
    @property
    def __name__(self):
        return self.__class__.__name__
    
    def process_step(self, request, form, step):
        if step == 0:
            form_string = str(form)
            attr = 'name="0-gravar" value='
            attr_pos = form_string.find(attr) + len(attr)
            attr_pos += 1   
            val = form_string[attr_pos:attr_pos + 2]
            if not val == 'on':
                if SelectInputFormStreamRecorder in self.form_list:
                    self.form_list.remove(SelectInputFormStreamRecorder)
            else:
                if not SelectInputFormStreamRecorder in self.form_list:
                    self.form_list.insert(2, SelectInputFormStreamRecorder)
        
    def parse_params(self, request, admin=None, *args, **kwargs):
        import os
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        from django.conf import settings
        
        skip_recorder = False
        if not request.POST.get('0-gravar') == 'on':
            skip_recorder = True
        logo_name = '4-logo'
        if skip_recorder:
            logo_name = '3-logo'
        if request.FILES:
            data = request.FILES[logo_name]
            path = default_storage.save('imgs/canal/logo/tmp/'\
                + str(data), ContentFile(data.read()))
            path_thumb = default_storage.save('imgs/canal/logo/thumb/'\
                + str(data), ContentFile(data.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            tmp_file = os.path.join(settings.MEDIA_ROOT, path_thumb)
        self._model_admin = admin
        opts = admin.model._meta
        
        step = request.POST.get('wizard_step')
        
        # Step's Title
        title = {None: 'Entrada de Fluxo',
                  '0': 'Entrada Demultiplexada'}
        
        if not skip_recorder:
            title.update({'1': 'Gravador de Fluxo',
                          '2': 'Cadastrar Ip de Saída',
                          '3': 'Adicionar Canal',
                          '4': None})
        else:
            title.update({'1': 'Cadastrar Ip de Saída',
                          '2': 'Adicionar Canal',
                          '3': None})
        title = title[step]
        
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

        return super(CanalCreationWizard, self).parse_params(request, admin)
    
    def render_template(self, request, form, previous_fields, step, \
                        context=None, step_title=None):
        from django.contrib.admin.helpers import AdminForm
        
        # Solucao para verificar se field foi preenchido
        skip_recorder = False
        if not step == 0:
            attr = 'name="0-gravar" value='
            attr_pos = previous_fields.find(attr) + len(attr)
            attr_pos += 1   
            val = previous_fields[attr_pos:attr_pos + 2]
            if val == 'on':
                skip_recorder = False
                
#        # Branch instead removing step        
#        if step == 2 and not skip_recorder:
#            form = self.get_form(step + 1)
#            step = step + 1
    
        # Wrap o formulario em um AdminForm para termos o fieldset
        form = AdminForm(form, [(
            'Passo %d de %d' % (step + 1, self.num_steps()),
            {'fields': form.base_fields.keys()}
            )], {})
        context = context or {}
        context.update({
            'media': self._model_admin.media + form.media
        })
        
        return super(CanalCreationWizard, self).render_template(
            request, form, previous_fields, step, context)
        
    def done(self, request, form_list):
        skip_recorder = False
        if not request.POST.get('0-gravar') == 'on':
            skip_recorder = True
        
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
            
        dvblast = Dvblast.objects.create(
            server=data['server'],
            name=data['name'],
            ip=data['ip'],
            port=data['port'],
            is_rtp=data['is_rtp'],
        )
        
        demuxedservice = DemuxedService.objects.create(
            server=data['server'],
            sid=data['sid'],
            provider=data['provider'],
            service_desc=data['service_desc'],
            enabled=data['enabled'],
            content_type_id=request.POST['1-content_type'],
            object_id=request.POST['1-object_id'],
        )
        
        if not skip_recorder:
            streamrecorder = StreamRecorder.objects.create(
                keep_time=data['keep_time'],
                rotate=data['rotate'],
                description=data['description'],
                start_time=data['start_time'],
                nic_sink=data['nic_sink'],
                object_id=data['object_id'],
                server=data['server'],
                content_type=data['content_type'],
                channel=data['channel'],
            )
            
        content_type = '3-content_type'
        if skip_recorder:
            content_type = '2-content_type'
        multicastoutput = MulticastOutput.objects.create(
           server=data['server'],
           content_type_id=request.POST[content_type],
           object_id=data['object_id'],
           interface=data['interface'],
           port=data['port'],
           protocol=data['protocol'],
           ip=data['ip'],
           nic_sink=data['nic_sink'],
        )
        
        logo_name = '4-logo'
        source_id_name = '4-source'
        epg_id = '4-epg'
        if skip_recorder:
            logo_name = '3-logo'
            source_id_name = '3-source'
            epg_id = '3-epg'
        logo = ''
        thumb = ''
        if request.FILES:
            logo = 'imgs/canal/logo/tmp/' + str(request.FILES[logo_name])
            thumb = 'imgs/canal/logo/thumb/' + str(request.FILES[logo_name])
        canal = Canal.objects.create(
           numero=data['numero'],
           nome=data['nome'],
           sigla=data['sigla'],
           logo=logo,
           thumb=thumb,
           source_id=request.POST[source_id_name],
           epg_id=request.POST[epg_id],
           enabled=data['enabled'],
        )
        
        return self._model_admin.response_add(request, canal)


create_canal_wizard = CanalCreationWizard([SelectInputFormDvblast,
                                           SelectInputFormDemuxedService,
                                           SelectInputFormMulticast,
                                           CanalForm])