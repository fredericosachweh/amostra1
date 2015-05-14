from django.contrib import admin

# Register your models here.

from cas.models import RTESServer
from cas.models import Device
from cas.models import Entitlement
from cas.models import DeviceEntitlement

class RTESServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'host')
    def has_add_permission(self, request):
        # if there's already an entry, do not allow adding
        count = RTESServer.objects.all().count()
        if count == 0:
            return True
        return False

# Device e Entitlement somente para validacao, apos testes deletar
#admin.site.register(Device)
#admin.site.register(Entitlement)
#admin.site.register(DeviceEntitlement)


admin.site.register(RTESServer, RTESServerAdmin)

