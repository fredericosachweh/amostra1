from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.doc import documentation_view
from handlers import *

channel_handler = Resource(ChannelHandler)
programme_handler = Resource(ProgrammeHandler)
guide_handler = Resource(GuideHandler)

channel_filters = ""
for c in channel_fields.iterkeys():
    channel_filters += c + '|'
channel_filters = channel_filters[:-1]  # Remove the last '|'

programme_filters = ""
for p in programme_fields.iterkeys():
    programme_filters += p + '|'
programme_filters = programme_filters[:-1]  # Remove the last '|'

urlpatterns = patterns('',

    # REST interface for channel resources
    url(r'^channels/?$', channel_handler),
    url(r'^channels/(?P<fields>((%s)(,)*)+)/?$' % channel_filters, channel_handler),
    url(r'^channels/(?P<channel_ids>(\d+(,)*)+)/?$', channel_handler),
    url(r'^channels/(?P<channel_ids>\d+)/(?P<fields>((%s)(,)*)+)/?$' % channel_filters, channel_handler, name='channel_handler'),

    # REST interface for programme resources
    url(r'^programmes/?$', programme_handler),
    url(r'^programmes/(?P<fields>((%s)(,)*)+)/?$' % programme_filters, programme_handler),
    url(r'^programmes/(?P<programme_ids>(\d+(,)*)+)/?$', programme_handler),
    url(r'^programmes/(?P<programme_ids>\d+)/(?P<fields>((%s)(,)*)+)/?$' % programme_filters, programme_handler, name='programme_handler'),

    # REST interface for guide resources
    url(r'^guide/?$', guide_handler),
    url(r'^guide/(?P<obj>(channels|programmes))/(?P<ids>(\d+(,)*)+)/?$', guide_handler, name='guide_handler'),

    # Auto generated documentation
    url(r'^$', documentation_view),

)
