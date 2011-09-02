from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#from django.conf import settings
#from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'site_multicat.views.home', name='home'),
    # url(r'^site_multicat/', include('site_multicat.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^static/extra/(.*)$', 'django.views.static.serve',{'document_root': settings.STATIC_ROOT,'show_indexes':True}),
    #url(r'^static_admin/(.*)$', 'django.views.static.serve',{'document_root': settings.STATIC_ROOT,'show_indexes':True}),
    url(r'^$','process.views.home'),
    url(r'^process/',include('process.urls')),
    #static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
)
urlpatterns += staticfiles_urlpatterns()