from django.contrib import admin
from models import *

class AdminVirtualChannel(admin.ModelAdmin):
    list_display = ('name', 'physical_channel', 'number', 'city', 'state')

class AdminDvbsChannel(admin.ModelAdmin):
    list_display = ('name', 'transponder', 'codec', 'definition', 'crypto', 'category')

admin.site.register(DvbsChannel, AdminDvbsChannel)
admin.site.register(VirtualChannel, AdminVirtualChannel)
