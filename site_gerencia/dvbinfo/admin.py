from django.contrib import admin
from models import *

class AdminVirtualChannel(admin.ModelAdmin):
    "ModelAdmin subclass for Brazillian digital TV channels"
    list_display = ('name', 'frequency', 'physical_channel', 'number', 'city', 'state')
    search_fields = ['name']
    list_filter = ('physical_channel__city__state',)

class AdminDvbsChannel(admin.ModelAdmin):
    "ModelAdmin subclass for satellite DVB channels"
    list_display = ('name', 'transponder', 'codec', 'definition', 'crypto', 'category')
    search_fields = ['name']
    list_filter = ('crypto', 'definition', 'codec', 'category', 'transponder__satellite', 'transponder__band')

admin.site.register(DvbsChannel, AdminDvbsChannel)
admin.site.register(VirtualChannel, AdminVirtualChannel)
