from django.contrib.formtools.wizard import FormWizard
from django.utils.encoding import force_unicode
from forms import *
from device.models import *
from canal.models import *

class CanalCreationWizard(FormWizard):
    @property
    def __name__(self):
        return self.__class__.__name__

    def parse_params(self, request, admin=None, *args, **kwargs):
        self._model_admin = admin # Save this so we can use it later.
        opts = admin.model._meta # Yes, I know we could've done Employer._meta, but this is cooler :)
        self.extra_context.update({
            'title': u'Add %s' % force_unicode(opts.verbose_name),
            'current_app': admin.admin_site.name,
            'has_change_permission': admin.has_change_permission(request),
            'add': True,
            'opts': opts,
            'root_path': admin.admin_site.root_path,
            'app_label': opts.app_label,
        })
    
    def render_template(self, request, form, previous_fields, step, context=None):
        from django.contrib.admin.helpers import AdminForm
        # Wrap this form in an AdminForm so we get the fieldset stuff:
        form = AdminForm(form, [(
            'Step %d of %d' % (step + 1, self.num_steps()),
            {'fields': form.base_fields.keys()}
            )], {})
        context = context or {}
        context.update({
            'media': self._model_admin.media + form.media
        })
        return super(CanalCreationWizard, self).render_template(request, form, previous_fields, step, context)

    def process_step(self, request, form, step):
        if step == 0 and hasattr(form, 'cleaned_data'):
            if form.cleaned_data['server'].is_local:
                return
            else:
                self.form_list.pop()
                if form.cleaned_data['server'].server_type == 'dvb':
                    self.form_list.append(ConfigureTunerInputForm)
                
        if step == 1 and hasattr(form, 'cleaned_data'):
            if form.cleaned_data['input_type'] == 'dvb-s':
                self.form_list.append(ConfigureTunerInputForm)
            elif form.cleaned_data['input_type'] == 'dvb-t':
                self.form_list.append(ConfigureTunerInputForm)

    def done(self, request, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        
        canal = Canal()
#        # First, create user:
#        user = User(
#            username=data['username'],
#            first_name=data['first_name'],
#            last_name=data['last_name'],
#            email=data['email']
#        )
#        user.set_password(data['password1'])
#        user.save()
#        # Next, create employer:
#        employer = Employer.objects.create(
#            user=user,
#            company_name=data['company_name'],
#            address=data['address'],
#            company_description=data.get('company_description', ''),
#            website=data.get('website', '')
#        )
        # Display success message and redirect to changelist:
        return self._model_admin.response_add(request, canal)

create_canal_wizard = CanalCreationWizard([SelectInputServerForm,SelectInputTypeForm,])

