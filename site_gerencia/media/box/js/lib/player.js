Ext.ns('Cianet.ux');

Cianet.ux.movies = new Array();
Cianet.ux.movies.filter = function(number){
	for (var i=0;i<this.length;i++)
	{
		var chrN = ''+this[i].numero;
		if (chrN.indexOf(''+number) == -1)
		{
			Cianet.ux.movies.selectNext();
			this[i].hide();
		}
	}
};
Cianet.ux.movies.showAll = function(){
	for (var i=0;i<this.length;i++)
	{
		this[i].show();
	}
};
Cianet.ux.movies.removeAll = function(){
	var l = this.length;
	for (var i=0;i<l;i++)
	{
		var d = this.pop();
		d.destroy();
		d = null;
	}
};
Cianet.ux.movies.getSelected = function(){
	for (var i=0;i<this.length;i++){
		if (this[i].selected){
			return this[i];
		}
	}
};
Cianet.ux.movies.selectNext = function(){
	var el = null;
	for (var i=0;i<this.length;i++){
		if (this[i].selected){
			// Verify if has next
			if (this.length > (i+1)){
				if (!this[i+1].isVisible)
					i++;
				this[i].leave();
				el = this[i+1];
				el.select();
				return el;
			}
			else {
				return this[i];
			}
		}
	}
};
Cianet.ux.movies.selectPrevius = function(){
	var el = null;
	for (var i=0;i<this.length;i++){
		if (this[i].selected){
			// Verify if has previous
			if (i > 0){
				if (!this[i-1].isVisible)
					i--;
				this[i].leave();
				el = this[i-1];
				el.select();
				return el;
			}
			else {
				return this[i];
			}
		}
	}
};










//Player status
Cianet.ux.PlayerState = {
	fullscreen:true,
	plaing:false,
	info:false,
	filtering:false,
	reload:false,
	osd:false
};





/**
 * OSD Controller
 */
Cianet.ux.osd = {
	setEl : function(el){
		el.setVisibilityMode(Ext.Element.DISPLAY);
		this.el = el;
	},
	setMovie : function(movie){
		this.tpl = new Ext.Template(
			[
				'<img class="logo" src="{img}" />',
				'<div class="numero">{numero}</div>',
			]);
		this.tpl.overwrite(this.el,{
			img:movie.img,
			numero:movie.numero
		});
	},
	show : function(){
		debug('osd.show');
		this.el.setVisible(true);
		Cianet.ux.PlayerState.osd = true;
		try {
			caMediaPlayer.toSetOsdOpacity(220);
		}catch(e){
			debug(e);
		}
	},
	hide : function(){
		debug('osd.hide');
		this.el.setVisible(false);
		Cianet.ux.PlayerState.osd = false;
		try {
			caMediaPlayer.toSetOsdOpacity(0);
		}catch(e){
			debug(e);
		}
	},
	toogle : function (){
		if (Cianet.ux.PlayerState.osd == true){
			this.hide();
		} else {
			this.show();
		}
	}
};//END: Cianet.ux.osd = {


Cianet.ux.medialist = {
	el:{setVisible:function(){}},
	setEl : function(el){
		el.setVisibilityMode(Ext.Element.DISPLAY);
		this.el = el;
	},
	toogle : function(){
		var visible = this.el.isVisible();
		if (visible){
			this.hide();
		} else {
			this.show();
		}
	},
	show : function(){
		debug('list.show');
		this.el.setVisible(true);
	},
	hide : function(){
		debug('list.hide');
		this.el.setVisible(false);
	}
};//END: Cianet.ux.medialist = {




Cianet.ux.mediainfo = {
	setEl : function(el){
		el.setVisibilityMode(Ext.Element.DISPLAY);
		this.el = el;
	},
	setMovie : function(movie){
		this.tpl = new Ext.Template(
			[
				'<img class="logo" src="{img}" />',
				'<div class="numero">{numero}</div>',
				'<div class="nome">{nome}</div>',
				'<div class="descricao"><pre>{descricao}</pre></div>',
				'<div class="ip">{ip}:{porta}</div>'
			]);
		this.tpl.overwrite(this.el,{
			id:movie.id,
			url:movie.url,
			nome:movie.fields.nome,
			numero:movie.fields.numero,
			descricao:movie.fields.descricao,
			img:movie.img,
			ip:movie.ip,
			porta:movie.porta,
			stype:movie.stype
		});
	},
	toogle : function(){
		var visible = this.el.isVisible();
		if (visible){
			this.hide();
		} else {
			this.show();
		}
	},
	show : function(){
		this.el.setVisible(true);
		try {
			caMediaPlayer.toSetPositionAndSize(1000,70,800,400);
			caMediaPlayer.toPlayerInfo( 1 );
		}catch(e){
			debug(e);
		}
	},
	hide : function(){
		this.el.setVisible(false);
		try {
			if (Cianet.ux.PlayerState.plaing == false){
				Cianet.ux.medialist.show();
			}
			caMediaPlayer.toSetFullScreen();
			Cianet.ux.PlayerState.fullscreen = true;
			caMediaPlayer.toPlayerInfo( 0 );
		}catch(e){
			debug(e);
		}
	}
}//END: Cianet.ux.mediainfo = {

















/**
 * Class to handle movie element
 */
Cianet.ux.Movie = Ext.extend(Ext.util.Observable, {
	el:null,
	width: null,
	height: null,
	x:0,
	y:0,
	fullScreen:false,
	selected:false,
	isVisible:true,
	constructor : function(config) {
		config = config || {};
		Ext.apply(this, config);
		Cianet.ux.Movie.superclass.constructor.call(this, config);
		this.addEvents(
			'play',
			'stop',
			'pause',
			'select',
			'leave',
			'info',
			'fullscreen',
			'repeat'
			);
		this.init();
		return this;
	},
	init : function() {
		this.id = this.fields.numero;//+Math.random();
		this.url = 'udp://'+this.fields.ip+':'+this.fields.porta;
		this.stype = 'mcast';
		this.nome = this.fields.nome;
		this.ip = this.fields.ip;
		this.porta = this.fields.porta;
		this.numero = this.fields.numero;
		//this.img = '/media/'+this.fields.thumb+'?'+Math.random();
		this.img = MEDIA_URL+''+this.fields.thumb

		this.movieTemplate = new Ext.Template(
			[
				'<div id="movie_{id}" class="movie">',
				'<div class="stype">{stype}</div>',
				'<div class="name">{numero} - {nome}</div>',
				'<img class="photo" src="{img}" />',
				'<div class="ip">{ip}:{porta}</div>',
				'</div>'
			]);
		this.el = Ext.get(this.movieTemplate.append('movies',{
			id:this.id,
			url:this.url,
			nome:this.fields.nome,
			numero:this.fields.numero,
			img:this.img,
			ip:this.ip,
			porta:this.porta,
			stype:this.stype
			}));
		this.el.setVisibilityMode(Ext.Element.DISPLAY);
	},
	play : function() {
		debug('movie.play');
		try {
			if (this.mtype == 'vod'){
				debug('VOD',this.url);
				var plaing = caMediaPlayer.toPlay(this.url,1,0);
			}
			else{
				debug('MULTICAST','udp://'+this.ip+':'+this.porta);
				var plaing = caMediaPlayer.toPlay('udp://'+this.ip+':'+this.porta,2,0);
			}
			//var plaing = caMediaPlayer.toPlay(this.url,1,0);
			Cianet.ux.PlayerState.plaing = true;
		} catch (e) {
			debug(e);
		}
		this.fireEvent('play');
	},
	stop : function() {
		debug('movie.stop');
		try {
			Cianet.ux.PlayerState.plaing = false;
			caMediaPlayer.toStop();
			caMediaPlayer.toExit();
		} catch (e) {
			debug(e);
		}
		this.fireEvent('stop');
	},
	select : function() {
		debug('movie.select');
		this.el.addClass('selected');
		this.selected = true;
		this.fireEvent('select');
	},
	leave : function() {
		debug('movie.leave');
		this.el.removeClass('selected');
		this.selected = false;
		this.fireEvent('leave');
	},
	fullScreen : function(){
		debug('movie.fullScreen');
		try {
			if (Cianet.ux.PlayerState.fullscreen == true){
				caMediaPlayer.toSetPositionAndSize(50,50,600,400);
				Cianet.ux.PlayerState.fullscreen = false;
			}else {
				caMediaPlayer.toSetFullScreen();
				Cianet.ux.PlayerState.fullscreen = true;
			}
		} catch (e){
			debug(e);
		}
		this.fireEvent('fullscreen');
	},
	repeat : function(){
		debug('movie.repeat');
		try {
			if( caMediaPlayer.toGetRepeatMode() )
				caMediaPlayer.toSetRepeatMode( false );
			else
				caMediaPlayer.toSetRepeatMode( true );
		} catch (e){
			debug(e);
		}
		this.fireEvent('repeat');
	},
	info : function(){
		debug('movie.info');
		try {
			var info = caMediaPlayer.toGetStreamInfo();
			debug('info',info);
		} catch (e){
			debug(e);
		}
		this.fireEvent('info');
	},
	hide : function(){
		debug('movie.hide');
		this.el.setVisible(false);
		this.isVisible = false;
	},
	show : function(){
		debug('movie.show');
		this.el.setVisible(true);
		this.isVisible = true;
	},
	destroy : function(){
		debug('movie.destroy');
		this.el.removeAllListeners();
		this.el.remove();
		purge(this);
	}
});//END: Cianet.ux.Movie = Ext.extend(Ext.util.Observable, {


/**
 * Timed task to hide OSD
 */
var task = new Ext.util.DelayedTask(function(){
	Cianet.ux.osd.hide();
});

function loadMedia(){
	if (Cianet.ux.PlayerState.reload == true)
		return;
	var selected = Cianet.ux.movies.getSelected();
	if (selected != undefined)
		var numero = selected.numero;
	else
		var numero = -1;
	Ext.Ajax.request({
		url : 'canal_list/',
		failure: function(resp,obj) {
			debug('Falhou',resp);
		},
		// Handler[success]
		success : function(resp, obj) {
			Cianet.ux.movies.removeAll();
			resObject = Ext.util.JSON.decode(resp.responseText);
			vod_playlist = resObject.data;
			for ( var i = 0; i < vod_playlist.length; i++) {
				var movie = new Cianet.ux.Movie(vod_playlist[i]);

				// Event[play]
				movie.on('play',function(){
					Cianet.ux.mediainfo.setMovie(this);
					Cianet.ux.medialist.hide();
					Cianet.ux.osd.setMovie(this);
					Cianet.ux.osd.show();
					Cianet.ux.mediainfo.hide();
					task.delay(7000);
				},movie);

				// Event[stop]
				movie.on('stop',function(){
					Cianet.ux.mediainfo.hide();
					Cianet.ux.osd.hide();
					Cianet.ux.medialist.show();
				},movie);

				// Event[select]
				movie.on('select',function(){
					// Set the scroll position on page
					var scroll = Cianet.ux.medialist.el.getScroll();
					var y = this.el.getY();
					Cianet.ux.medialist.el.scrollTo('top',(y+scroll.top-500));
					Cianet.ux.osd.setMovie(this);
					Cianet.ux.mediainfo.setMovie(this);
				},movie);

				// Event[info]
				movie.on('info',function(){
					Cianet.ux.mediainfo.setMovie(this);
					Cianet.ux.medialist.hide();
					Cianet.ux.osd.hide();
					Cianet.ux.mediainfo.toogle();
				},movie);

				// Event[fullscreen]
				movie.on('fullscreen',function(){
					//Cianet.ux.mediainfo.toogle();
				},movie);

				Cianet.ux.movies.push(movie);
				if (numero == movie.numero)
					movie.select();
			}
			if (numero == -1)
				Cianet.ux.movies[0].select();
			Cianet.ux.PlayerState.reload = false;
		}
	});//END: Ext.Ajax.request({

}//END: function loadMedia(){


/*
 *
object name: caNetConfigObj
1. caNetConfigObj.Sayhello -> the same as other object; an easy way to verify this object could work well with Java Script
2. caNetConfigObj.Getversion -> return the version string
3. caNetConfigObj.GetNetPropertyToCache -> In java script, we can't use structure as we do everyday in c/c++, so we have to set/get one property each time. This doesn't make sense for our library to do this, so we have a cache in our design. To get properties back, call this function first. This function will save all the network information at cache.
Note: we may improve this part in the near future. This means you can set/get value by our object's fields independently.
4. caNetConfigObj.GetNetProperty -> Calling this function with type parameter gets property back.
Get mac = 1, get ip = 2, get netmask = 3, get gateway = 4, get dns = 5.
5. caNetConfigObj.CleanValid -> As the get property, we have the cache design inside also. To set network property, first call this function before doing any setting.
6. caNetConfigObj.SetNetProperty -> Calling this function with type and value sets property to network. However, this won't set to system until calling the function below.
7. caNetConfigObj.SetNetPropertyToNetwork -> Calling this function sets the network property to network.
8. caNetConfigObj.SetNetDHCP -> This function is for dhcp usage only. When want to set network by dhcp, just call this fuction with time out parameter.
 */
function netInfo()
{
	var ret = '';
	ret += 'Version= '+caNetConfigObj.Getversion()+'\n';
	caNetConfigObj.GetNetPropertyToCache();
	var property=caNetConfigObj.GetNetProperty(1);
	ret += "MACADDR= "+property+'\n';
	property=caNetConfigObj.GetNetProperty(2);
	ret += "IP= "+property+'\n';
	property=caNetConfigObj.GetNetProperty(3);
	ret += "NETMASK= "+property+'\n';
	property=caNetConfigObj.GetNetProperty(4);
	ret += "GATEWAY= "+property+'\n';
	property=caNetConfigObj.GetNetProperty(5);
	ret += "LOCAL= "+property+'\n';
	debug(ret);
	return ret;
}

function getIP()
{
	try {
		// You will see the message in your console
		caFileBrowseObj.Sayhello("JS check file browser object");
		//var ver=caFileBrowseObj.Getversion();
		alert(netInfo());
		// try our netconfig object
		//alert("============== Set Static IP ==============");
		//caNetConfigObj.CleanValid();
		//caNetConfigObj.SetNetProperty(2, "192.168.0.77");
		//caNetConfigObj.SetNetProperty(3, "255.255.255.0");
		//caNetConfigObj.SetNetProperty(4, "192.168.0.1");
		//caNetConfigObj.SetNetProperty(5, "127.0.0.1");
		//caNetConfigObj.SetNetPropertyToNetwork();
		//caNetConfigObj.GetNetPropertyToCache();
		//alert(netInfo());
		alert("============== Set DHCP ==============");
		caNetConfigObj.CleanValid();
		//caNetConfigObj.GetNetPropertyToCache();
		caNetConfigObj.SetNetDHCP(10);
		alert('Setado DHCP');
		alert(netInfo());
		//caNetConfigObj.SetNetPropertyToNetwork();
		//caNetConfigObj.GetNetPropertyToCache();
	}catch(e){
		debug(e);
	}
}

var channel_updater = {
	stress:false,
	run:function(){
		Ext.Ajax.request({
			url : 'canal_update/',
			// Handler[failure]
			failure: function(resp,obj) {
				debug('Fail on load service',resp);
			},
			// Handler[success]
			success : function(resp, obj) {
				resObject = Ext.util.JSON.decode(resp.responseText);
				var atualizado = new Date(resObject.atualizado);
				if (this.stress == true)
				{
					loadMedia();
					return;
				}
				if (atualizado > this.ultimo)
				{
					this.ultimo = atualizado;
					loadMedia();
				}
			},
			scope:this
		});
	},
	ultimo:new Date('Wed, 18 Oct 2000 13:00:00 EST'),
	interval:300*1000
};




Ext.onReady(function() {
	if (stressJS)
	{
		channel_updater.interval = 1*1000;
		channel_updater.stress = true;
	}
	else
	{
		channel_updater.interval = 300*1000;
		channel_updater.stress = false;
	}

	// Estados iniciais
	Cianet.ux.PlayerState.plaing = false;
	Cianet.ux.PlayerState.osd = false;
	var DOC = Ext.get(document);
	// Informações da midia
	Cianet.ux.mediainfo.setEl(Ext.get('mediainfo'));
	Cianet.ux.mediainfo.hide();
	// OSD
	Cianet.ux.osd.setEl(Ext.get('osd'));
	Cianet.ux.osd.hide();
	// Listagem de midias
	Cianet.ux.medialist.setEl(Ext.get('movies'));
	Cianet.ux.medialist.show();
	// Call load media list from webservice
	Ext.TaskMgr.start(channel_updater);

	// Handler[keypress]
	DOC.on('keypress', function(event, opt) {
		var key = event.getKey();

		// TODO: browse channels on numeric key
		if ( (Browser.KEY.N_0) <= key && Browser.KEY.N_9 >= key){
			//debug('Numeric',event,opt);
		}

		switch (key) {
		case Browser.KEY.n:
			getIP();
			break;
		case Browser.KEY.o:
			var selected = Cianet.ux.movies.getSelected();
			Cianet.ux.osd.setMovie(selected);
			Cianet.ux.osd.toogle();
			break;
		case Browser.KEY.i:
			Cianet.ux.movies.getSelected().info();
			break;
		case Browser.KEY.INFO:
			Cianet.ux.movies.getSelected().info();
			break;
		case Browser.KEY.r:
			Cianet.ux.movies.getSelected().repeat();
			break;
		case Browser.KEY.f:
			var selected = Cianet.ux.movies.getSelected();
			selected.fullScreen();
			break;
		case Browser.KEY.p:
			var selected = Cianet.ux.movies.getSelected();
			selected.play();
			break;
		case Browser.KEY.ENTER:
			var selected = Cianet.ux.movies.getSelected();
			selected.play();
			break;
		case Browser.KEY.s:
			var selected = Cianet.ux.movies.getSelected();
			selected.stop();
			break;
		case Browser.KEY.RETURN:
			var selected = Cianet.ux.movies.getSelected();
			selected.stop();
			break;
		case Browser.KEY.DOWN:
			Cianet.ux.movies.selectNext();
			break;
		case Browser.KEY.UP:
			Cianet.ux.movies.selectPrevius();
			break;
		case Browser.KEY.RIGHT:
			var running = Cianet.ux.movies.getSelected();
			running.stop();
			Cianet.ux.mediainfo.hide();
			var movie = Cianet.ux.movies.selectNext();
			movie.play();
			break;
		case Browser.KEY.LEFT:
			var running = Cianet.ux.movies.getSelected();
			running.stop();
			var movie = Cianet.ux.movies.selectPrevius();
			movie.play();
			break;
		case Browser.KEY.HOME:
			loadMedia();
			break;
		}
		return false;
	}, this);
});//END: Ext.onReady(function() {


