from piston.handler import BaseHandler
from piston.utils import rc
from epg.models import Channel, Programme, Guide

# Defining the desired elements
channel_fields = {	'id' : 'id',
		'channelid' : 'channelid',
		'display_names' : ('display_names' ,('value', ('lang', ('value',)))),
		'icons' : ('icons', ('src',)),
		'urls' : 'urls' }

class ChannelHandler(BaseHandler):
	'''
	Handle channel resources
	'''
	allowed_methods = ('GET',)
	model = Channel
	fields = channel_fields.values()

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
			if param == 'display_names':
				base = base.filter(display_names__value__istartswith=request.GET[param])
			if param == 'icons':
				base = base.filter(icons__src__istartswith=request.GET[param])
			if param == 'urls':
				base = base.filter(urls__value__istartswith=request.GET[param])
	
		if channel_ids:
			return base.filter(pk__in=channel_ids.split(','))
		else:
			return base.all()

# Defining the desired elements
programme_fields = {	'id' : 'id',
		'programmeid' : 'programmeid',
		'titles' : ('titles' ,('value', ('lang', ('value',)))),
		'secondary_titles' : ('secondary_titles' ,('value', ('lang', ('value',)))),
		'descriptions' : ('descriptions' ,('value', ('lang', ('value',)))),
		'date' : 'date',
		'categories' : ('categories', ('value', ('lang', ('value',)))),
		'country' : ('country', ('value',)),
		'episode_numbers' : ('episode_numbers', ('value', 'system',)),
		'rating' : ('rating', ('system', 'value',)),
		'language' : ('language', ('value', ('lang', ('value',)))),
		'original_language' : ('original_language', ('value', ('lang', ('value',)))),
		'length' : 'length',
		'subtitles' : ('subtitles', ('value', ('lang', ('value',)))),
		'video_present' : 'video_present',
		'video_colour' : 'video_colour',
		'video_aspect' : 'video_aspect',
		'video_quality' : 'video_quality',
		'audio_present' : 'audio_present',
		'audio_stereo' : 'audio_stereo',
		'actors' : ('actors', ('name', 'role',)),
		'directors' : ('directors', ('name',)),
		'writers' : ('writers', ('name',)),
		'adapters' : ('adapters', ('name',)),
		'producers' : ('producers', ('name',)),
		'composers' : ('composers', ('name',)),
		'editors' : ('editors', ('name',)),
		'presenters' : ('presenters', ('name',)),
		'commentators' : ('commentators', ('name',)),
		'guests' : ('guests', ('name',)) }

class ProgrammeHandler(BaseHandler):
	'''
	Handle programme resources
	'''
	allowed_methods = ('GET',)
	model = Programme
	fields = programme_fields.values()

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
			if param == 'titles':
				base = base.filter(titles__value__istartswith=request.GET[param])
			if param == 'secondary_titles':
				base = base.filter(secondary_titles__value__istartswith=request.GET[param])
			if param == 'descriptions':
				base = base.filter(description__value__istartswith=request.GET[param])
			if param == 'date':
				base = base.filter(date__istartswith=request.GET[param])
			if param == 'categories':
				base = base.filter(categories__value__istartswith=request.GET[param])
			if param == 'country':
				base = base.filter(country__value__istartswith=request.GET[param])
			if param == 'episode_numbers':
				base = base.filter(episode_numbers__value__istartswith=request.GET[param])
			if param == 'rating':
				base = base.filter(rating__value__istartswith=request.GET[param])
			if param == 'language':
				base = base.filter(language__value__istartswith=request.GET[param])
			if param == 'original_language':
				base = base.filter(original_language__value__istartswith=request.GET[param])
			if param == 'length':
				base = base.filter(length=request.GET[param])
			if param == 'subtitles':
				base = base.filter(subtitles__value__istartswith=request.GET[param])
			if param == 'video_present':
				base = base.filter(video_present=request.GET[param])
			if param == 'video_colour':
				base = base.filter(video_colour=request.GET[param])
			if param == 'video_aspect':
				base = base.filter(video_aspect=request.GET[param])
			if param == 'video_quality':
				base = base.filter(video_quality=request.GET[param])
			if param == 'audio_present':
				base = base.filter(audio_present=request.GET[param])
			if param == 'audio_stereo':
				base = base.filter(audio_stereo=request.GET[param])
			if param == 'actors':
				base = base.filter(actors__name__istartswith=request.GET[param])
			if param == 'directors':
				base = base.filter(directors__name__istartswith=request.GET[param])
			if param == 'writers':
				base = base.filter(writers__name__istartswith=request.GET[param])
			if param == 'adapters':
				base = base.filter(adapters__name__istartswith=request.GET[param])
			if param == 'producers':
				base = base.filter(producers__name__istartswith=request.GET[param])
			if param == 'composers':
				base = base.filter(composers__name__istartswith=request.GET[param])
			if param == 'editors':
				base = base.filter(editors__name__istartswith=request.GET[param])
			if param == 'presenters':
				base = base.filter(presenters__name__istartswith=request.GET[param])
			if param == 'commentators':
				base = base.filter(commentators__name__istartswith=request.GET[param])
			if param == 'guests':
				base = base.filter(guests__name__istartswith=request.GET[param])

		if programme_ids:
			return base.filter(pk__in=programme_ids.split(','))
		else:
			return base.all()
			
# Defining the desired elements
guide_fields = {	'programme' : 'programme_id',
		'channel' : 'channel_id',
		'start' : 'start',
		'stop' : 'stop' }

class GuideHandler(BaseHandler):
	'''
	Handle guide resources
	'''
	allowed_methods = ('GET',)
	model = Guide
	fields = guide_fields.values()

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
				base = base.filter(start__gte=parse(request.GET[param]))
			if param == 'stop':
				base = base.filter(stop__lte=parse(request.GET[param]))
				
		if (ids and obj):
			if obj == 'channels':
				return base.filter(channel__in=ids.split(','))
			if obj == 'programmes':
				return base.filter(programme__in=ids.split(','))
		else:
			return base.all()

