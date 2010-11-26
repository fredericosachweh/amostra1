Ext.ns('Cianet.ux');

Cianet.ux.movies = new Array();
Cianet.ux.movies.filter = function(number){
	var l = Ext.get(this);
	l.each(function(){
		//debug('--->',this);
		if (this.id == number) {
			//debug('Ocultando',this.id);
			Ext.get(this).hide();
			//this.hide();
		}
	});
}
Cianet.ux.movies.getSelected = function(){
	for (var i=0;i<this.length;i++){
		if (this[i].selected){
			return this[i];
		}
	}
}
Cianet.ux.movies.selectNext = function(){
	var el = null;
	for (var i=0;i<this.length;i++){
		if (this[i].selected){
			// Verifica se tem proximo
			if (this.length > (i+1)){
				this[i].leave();
				el = this[i+1];
				el.select();
				return el;
			}
		}
	}
}
Cianet.ux.movies.selectPrevius = function(){
	var el = null;
	for (var i=0;i<this.length;i++){
		if (this[i].selected){
			// Verifica se tem proximo
			if (i > 0){
				this[i].leave();
				el = this[i-1];
				el.select();
				return el;
			}
		}
	}
}


Cianet.ux.mediainfo = {
	el:null,
	setEl : function(el){
		this.el = el;
	},
	setMovieName : function(name){
		Ext.fly('moviename').update(name);
	},
	setMovieHost : function(host){
		Ext.fly('moviehost').update(host);
	},
	setMoviePort : function(port){
		Ext.fly('movieport').update(port);
	},
	setMovieId : function(id){
		Ext.fly('movieid').update(id);
	},
	toogle : function(){
		var w = this.el.getWidth(true);
		debug('W='+w);
		if (w != 0){
			this.hide();
		} else {
			this.show();
		}
	},
	show : function(){
		debug('Exibindo');
		this.el.setWidth(200,true);
	},
	hide : function(){
		debug('Ocultando');
		this.el.setWidth(0,true);
	}
}

// Player status
Cianet.ux.PlayerState = {
	fullscreen:true,
	plaing:false,
	info:false,
	filtering:false
};



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
		this.id = this.pk+Math.random();
		this.url = 'udp://'+this.fields.ip+':'+this.fields.porta;
		this.stype = 'mcast';
		this.name = this.fields.nome;
		this.ip = this.fields.ip;
		this.porta = this.fields.porta;
		this.img = '/media/'+this.fields.thumb;

		this.movieTemplate = new Ext.Template(
			[
				'<div id="movie_{id}" class="movie">',
				'<div class="stype">{stype}</div>',
				//'<a href="{url}" >',
				'<div class="name">{name}</div>',
				'<img class="photo" src="{img}" />',
				//'</a>',
				'</div>'
			]);
		this.el = Ext.get(this.movieTemplate.append('movies',{id:this.id,url:this.url,name:this.name,img:this.img,stype:this.stype}));
	},
	play : function() {
		try {
			if (Cianet.ux.PlayerState.plaing){
				caMediaPlayer.toPause();
				Cianet.ux.PlayerState.plaing = false;
			} else {
				if (this.mtype == 'vod'){
					debug('VOD',this.url);
					var plaing = caMediaPlayer.toPlay(this.url,1,0);
				}
				else{
					debug('MULTICAST','udp://'+this.ip+':'+this.porta);
					var plaing = caMediaPlayer.toPlay('udp://'+this.ip+':'+this.porta,2,0);
				}
				//var plaing = caMediaPlayer.toPlay(this.url,1,0);
				Cianet.ux.PlayerState.plaing = plaing;
			}
		} catch (e) {}
		this.fireEvent('play');
	},
	stop : function() {
		try {
			caMediaPlayer.toStop();
			caMediaPlayer.toExit();
		} catch (e) {}
		this.fireEvent('stop');
	},
	select : function() {
		this.el.addClass('selected');
		this.selected = true;
		this.fireEvent('select');
	},
	leave : function() {
		this.el.removeClass('selected');
		this.selected = false;
		this.fireEvent('leave');
	},
	fullScreen : function(){
		try {
			if (Cianet.ux.PlayerState.fullscreen){
				caMediaPlayer.toSetPositionAndSize(50,50,600,400);
				Cianet.ux.PlayerState.fullscreen = false;
			}else {
				caMediaPlayer.toSetFullScreen();
				Cianet.ux.PlayerState.fullscreen = true;
			}
		} catch (e){}
		this.fireEvent('fullscreen');
	},
	repeat : function(){
		try {
			if( caMediaPlayer.toGetRepeatMode() )
				caMediaPlayer.toSetRepeatMode( false );
			else
				caMediaPlayer.toSetRepeatMode( true );
		} catch (e){}
		this.fireEvent('repeat');
	},
	info : function(){
		debug('Info');
		try {
			caMediaPlayer.toSetPositionAndSize(300,60,300,200);
			caMediaPlayer.toPlayerInfo( 1 );
			var info = caMediaPlayer.toGetStreamInfo();
			debug('info',info);
		} catch (e){}
		this.fireEvent('info');
	}
});//END: Cianet.ux.Movie = Ext.extend(Ext.util.Observable, {

var anim = {
	duration : 4,
	easing : 'easeIn',
	scope : anim
};

/**
 * Test function to animate html element
 */
function anime() {
	var a = Ext.get('an');
	Ext.fly('msg').update('Animation box....');
	if (a.getX() == 0)
		a.moveTo(830, 700, anim);
	else
		a.moveTo(0,0, anim);
};//END: function anime() {


function loadMedia(){
	Ext.Ajax.request({
		url : '/box/canal_list/',
		failure: function(resp,obj) {
			debug('Falhou',resp);
		},
		success : function(resp, obj) {
			resObject = Ext.util.JSON.decode(resp.responseText);
			var movies = Ext.get('movies');
			vod_playlist = resObject.data;
			for ( var i = 0; i < vod_playlist.length; i++) {
				var movie = new Cianet.ux.Movie(vod_playlist[i]);

				// Evento de play
				movie.on('play',function(){
					Ext.fly('msg').update('Rodando '+this.name);
					Ext.get('movies').hide();
					Cianet.ux.mediainfo.hide();
				},movie);

				// Evento de play
				movie.on('stop',function(){
					Ext.fly('msg').update('Parado '+this.name);
					Ext.get('movies').show();
					Cianet.ux.mediainfo.hide();
				},movie);

				// Evento de select
				movie.on('select',function(){
					// Ajusta o scroll da pagina
					var scroll = movies.getScroll();
					var y = this.el.getY();
					movies.scrollTo('top',(y+scroll.top-100));
				},movie);

				// Event [info]
				movie.on('info',function(){
					Cianet.ux.mediainfo.setMovieName(this.name);
					Cianet.ux.mediainfo.setMovieHost(this.ip);
					Cianet.ux.mediainfo.setMoviePort(this.porta);
					Cianet.ux.mediainfo.setMovieId(this.id);
					Cianet.ux.mediainfo.toogle();
				},movie);

				movie.on('fullscreen',function(){
					if (Cianet.ux.PlayerState.fullscreen == true){
						Cianet.ux.mediainfo.hide();
					}else {
						Cianet.ux.mediainfo.show();
					}
				},movie);

				Cianet.ux.movies.push(movie);
			}
			Cianet.ux.movies[0].select();
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

function getIP()
{
	// You will see the message in your console
	caFileBrowseObj.Sayhello("JS check file browser object");
	var ver=caFileBrowseObj.Getversion();
	alert(ver);
	// try our netconfig object
	ver=caNetConfigObj.Getversion();
	alert(ver);
	caNetConfigObj.GetNetPropertyToCache();
	var property=caNetConfigObj.GetNetProperty(1);
	alert("MAC= "+property);
	property=caNetConfigObj.GetNetProperty(2);
	alert("IP= "+property);
	property=caNetConfigObj.GetNetProperty(3);
	alert("NETMASK= "+property);
	property=caNetConfigObj.GetNetProperty(4);
	alert("GATEWAY= "+property);
	property=caNetConfigObj.GetNetProperty(5);
	alert("LOCAL= "+property);
	//alert("==============Set Static IP==============");
	//caNetConfigObj.CleanValid();
	//caNetConfigObj.SetNetProperty(2, "192.168.0.77");
	//caNetConfigObj.SetNetProperty(3, "255.255.255.0");
	//caNetConfigObj.SetNetProperty(4, "192.168.0.1");
	//caNetConfigObj.SetNetProperty(5, "189.77.236.2");
	//caNetConfigObj.SetNetPropertyToNetwork();
	alert("==============Set DHCP ==============");
	caNetConfigObj.CleanValid();
	CaNetConfigObj.SetNetDHCP(2);
	alert('Setado DHCP');
	//caNetConfigObj.SetNetPropertyToNetwork();
	//caNetConfigObj.GetNetPropertyToCache();
	var property=caNetConfigObj.GetNetProperty(1);
	alert("MAC= "+property);
	property=caNetConfigObj.GetNetProperty(2);
	alert("IP= "+property);
	property=caNetConfigObj.GetNetProperty(3);
	alert("NETMASK= "+property);
	property=caNetConfigObj.GetNetProperty(4);
	alert("GATEWAY= "+property);
	property=caNetConfigObj.GetNetProperty(5);
	alert("LOCAL= "+property);
}


Ext.onReady(function() {
	var DOC = Ext.get(document);
	Cianet.ux.mediainfo.setEl(Ext.get('mediainfo'));
	showAnim = {
		duration : 4
	};
	// Carrega a lista de midias via webservice
	//for (var i =0; i<10;i++)
	loadMedia();
	//
	DOC.on('keypress', function(event, opt) {
		var key = event.getKey();
		Ext.fly('an').update('KEY:'+key);
		debug('KEY= '+key+' ');

		if ( (Browser.KEY.N_0) <= key && Browser.KEY.N_9 >= key){
			debug('Numeric');
			//Cianet.ux.movies.filter(5);
		}

		switch (key) {
		case Browser.KEY.a:
			anime();
			break;
		case Browser.KEY.n:
			getIP();
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
		case Browser.KEY.RIGHT:
			Cianet.ux.movies.selectNext();
			break;
		case Browser.KEY.LEFT:
			Cianet.ux.movies.selectPrevius();
			break;
		case Browser.KEY.DOWN:
			var running = Cianet.ux.movies.getSelected();
			running.stop();
			var movie = Cianet.ux.movies.selectNext();
			movie.play();
			break;
		case Browser.KEY.UP:
			var running = Cianet.ux.movies.getSelected();
			running.stop();
			var movie = Cianet.ux.movies.selectPrevius();
			movie.play();
			break;
		case Browser.KEY.HOME:
			loadMedia();
			//window.location.href = '../placa/';
			break;
		}
		return false;
	}, this);
});//END: Ext.onReady(function() {


