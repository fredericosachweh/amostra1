from piston.handler import BaseHandler
from piston.utils import rc
from epg.models import Channel, Programme, Guide

# Defining the desired elements
channel_fields = {
    'id': 'id',
    'channelid': 'channelid',
    'display_names': ('display_names' ,('value', ('lang', ('value',)))),
    'icons': ('icons', ('src',)),
    'urls': 'urls'
}

class ChannelHandler(BaseHandler):
    '''
    Handle channel resources
    '''
    allowed_methods = ('GET',)
    model = Channel
    fields = channel_fields.values()

    @staticmethod
    def resource_uri():
        return ('channel_handler', ['id'])

    def read(self, request, channel_ids=None, fields=None):
        '''
        Returns a set of channel resources
        '''

        if fields:
            self.fields = [f for f in fields.split(',') if f]
            self.fields.append('id')

        base = Channel.objects

        # Query string for search
        for param in request.GET.iterkeys():
            if param == 'channelid':
                base = base.filter(channelid=request.GET[param])
            elif param == 'display_names':
                base = base.filter(display_names__value__istartswith=request.GET[param])
            elif param == 'icons':
                base = base.filter(icons__src__istartswith=request.GET[param])
            elif param == 'urls':
                base = base.filter(urls__value__istartswith=request.GET[param])
            elif param == 'limit' or param == 'page':
                continue
            else:
                return rc.BAD_REQUEST

        if channel_ids:
            ret = base.filter(pk__in=channel_ids.split(','))
        else:
            ret = base.all()

        if len(ret):
            return api_pagination(ret, request)
        else:
            return rc.NOT_FOUND


# Defining the desired elements
programme_fields = {
    'id': 'id',
    'programmeid': 'programmeid',
    'titles': ('titles' ,('value', ('lang', ('value',)))),
    'secondary_titles': ('secondary_titles' ,('value', ('lang', ('value',)))),
    'descriptions': ('descriptions' ,('value', ('lang', ('value',)))),
    'date': 'date',
    'categories': ('categories', ('value', ('lang', ('value',)))),
    'country': ('country', ('value',)),
    'episode_numbers': ('episode_numbers', ('value', 'system',)),
    'rating': ('rating', ('system', 'value',)),
    'language': ('language', ('value', ('lang', ('value',)))),
    'original_language': ('original_language', ('value', ('lang', ('value',)))),
    'length': 'length',
    'subtitles': ('subtitles', ('value', ('lang', ('value',)))),
    'video_present': 'video_present',
    'video_colour': 'video_colour',
    'video_aspect': 'video_aspect',
    'video_quality': 'video_quality',
    'audio_present': 'audio_present',
    'audio_stereo': 'audio_stereo',
    'actors': ('actors', ('name', 'role',)),
    'directors': ('directors', ('name',)),
    'writers': ('writers', ('name',)),
    'adapters': ('adapters', ('name',)),
    'producers': ('producers', ('name',)),
    'composers': ('composers', ('name',)),
    'editors': ('editors', ('name',)),
    'presenters': ('presenters', ('name',)),
    'commentators': ('commentators', ('name',)),
    'guests': ('guests', ('name',))
}


class ProgrammeHandler(BaseHandler):
    '''
    Handle programme resources
    '''
    allowed_methods = ('GET',)
    model = Programme
    fields = programme_fields.values()

    @staticmethod
    def resource_uri():
        return ('programme_handler', ['id'])

    def read(self, request, programme_ids=None, fields=None):
        '''
        Returns a set of programme resources
        '''

        if fields:
            self.fields = [f for f in fields.split(',') if f]
            self.fields.append('id')

        base = Programme.objects

        # Query string for search
        for param in request.GET.iterkeys():
            if param == 'programid':
                base = base.filter(programid=request.GET[param])
            elif param == 'titles':
                base = base.filter(titles__value__istartswith=request.GET[param])
            elif param == 'secondary_titles':
                base = base.filter(secondary_titles__value__istartswith=request.GET[param])
            elif param == 'descriptions':
                base = base.filter(description__value__istartswith=request.GET[param])
            elif param == 'date':
                base = base.filter(date__istartswith=request.GET[param])
            elif param == 'categories':
                base = base.filter(categories__value__istartswith=request.GET[param])
            elif param == 'country':
                base = base.filter(country__value__istartswith=request.GET[param])
            elif param == 'episode_numbers':
                base = base.filter(episode_numbers__value__istartswith=request.GET[param])
            elif param == 'rating':
                base = base.filter(rating__value__istartswith=request.GET[param])
            elif param == 'language':
                base = base.filter(language__value__istartswith=request.GET[param])
            elif param == 'original_language':
                base = base.filter(original_language__value__istartswith=request.GET[param])
            elif param == 'length':
                base = base.filter(length=request.GET[param])
            elif param == 'subtitles':
                base = base.filter(subtitles__value__istartswith=request.GET[param])
            elif param == 'video_present':
                base = base.filter(video_present=request.GET[param])
            elif param == 'video_colour':
                base = base.filter(video_colour=request.GET[param])
            elif param == 'video_aspect':
                base = base.filter(video_aspect=request.GET[param])
            elif param == 'video_quality':
                base = base.filter(video_quality=request.GET[param])
            elif param == 'audio_present':
                base = base.filter(audio_present=request.GET[param])
            elif param == 'audio_stereo':
                base = base.filter(audio_stereo=request.GET[param])
            elif param == 'actors':
                base = base.filter(actors__name__istartswith=request.GET[param])
            elif param == 'directors':
                base = base.filter(directors__name__istartswith=request.GET[param])
            elif param == 'writers':
                base = base.filter(writers__name__istartswith=request.GET[param])
            elif param == 'adapters':
                base = base.filter(adapters__name__istartswith=request.GET[param])
            elif param == 'producers':
                base = base.filter(producers__name__istartswith=request.GET[param])
            elif param == 'composers':
                base = base.filter(composers__name__istartswith=request.GET[param])
            elif param == 'editors':
                base = base.filter(editors__name__istartswith=request.GET[param])
            elif param == 'presenters':
                base = base.filter(presenters__name__istartswith=request.GET[param])
            elif param == 'commentators':
                base = base.filter(commentators__name__istartswith=request.GET[param])
            elif param == 'guests':
                base = base.filter(guests__name__istartswith=request.GET[param])
            elif param == 'limit' or param == 'page':
                continue
            else:
                return rc.BAD_REQUEST
        if programme_ids:
            ret = base.filter(pk__in=programme_ids.split(','))
        else:
            ret = base.all()
        if len(ret):
            return api_pagination(ret, request)
        else:
            return rc.NOT_FOUND

# Defining the desired elements
guide_fields = {
    'id': 'id',
    'programme': 'programme_id',
    'channel': 'channel_id',
    'start': 'start',
    'stop': 'stop'
}

class GuideHandler(BaseHandler):
    '''
    Handle guide resources
    '''
    allowed_methods = ('GET',)
    model = Guide
    fields = guide_fields.values()

    @staticmethod
    def resource_uri():
        return ('guide_handler', ['id'])

    def read(self, request, obj=None, ids=None, fields=None):
        '''
        Returns a set of guide resources
        '''
        if fields:
            self.fields = [f for f in fields.split(',') if f]
        base = Guide.objects
        # Query string for search
        from dateutil.parser import parse
        for param in request.GET.iterkeys():
            if param == 'start':
                base = base.filter(stop__gt=parse(request.GET[param]))
            elif param == 'stop':
                base = base.filter(start__lt=parse(request.GET[param]))
            elif param == 'limit' or param == 'page':
                continue
            else:
                return rc.BAD_REQUEST
        if (ids and obj):
            if obj == 'channels':
                ret = base.filter(channel__in=ids.split(','))
            elif obj == 'programmes':
                ret = base.filter(programme__in=ids.split(','))
            else:
                return rc.BAD_REQUEST
        else:
            ret = base.all()
        if len(ret):
            return api_pagination(ret, request)
        else:
            return rc.NOT_FOUND

# Handle pagination
def api_pagination(queryset, request):
    from django.core.paginator import Paginator
    from django.shortcuts import redirect

    limit = 50    # Maximum allowed
    page = 1

    if request.GET.has_key('limit'):
        if int(request.GET['limit']) > limit:
            return redirect('%s?limit=%d&page=%d' % (request.path,limit,page))
        else:
            limit = int(request.GET['limit'])
    else:
        if queryset.count() > limit:
            return redirect('%s?limit=%d&page=%d' % (request.path,limit,page))
        else:
            return queryset
    if request.GET.has_key('page'):
        page = int(request.GET['page'])
    p = Paginator(queryset, limit)
    if page > p.num_pages:
        return []
    else:
        return p.page(page).object_list


from piston.doc import generate_doc

doc = generate_doc(ChannelHandler)

for m in doc.get_methods():
    print m
    for a in m.iter_args():
        print a

print doc
