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
}
Cianet.ux.movies.showAll = function(){
	for (var i=0;i<this.length;i++)
	{
		this[i].show();
	}
}
Cianet.ux.movies.removeAll = function(){
	var l = this.length;
	for (var i=0;i<l;i++)
	{
		var d = this.pop();
		d.destroy();
	}
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
			// Verifica se existe o proximo
			if (this.length > (i+1)){
				if (!this[i+1].isVisible)
					i++;
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
			// Verifica se existe o anterior
			if (i > 0){
				if (!this[i-1].isVisible)
					i--;
				this[i].leave();
				el = this[i-1];
				el.select();
				return el;
			}
		}
	}
}









Cianet.ux.mediainfo = {
	setEl : function(el){
		el.setVisibilityMode(Ext.Element.DISPLAY);
		this.el = el;
	},
	setMovie : function(movie){
		this.template = new Ext.Template(
			[
				'<img class="logo" src="{img}" />',
				'<div class="numero">{numero}</div>',
				'<div class="nome">{nome}</div>',
				'<div class="descricao"><pre>{descricao}</pre></div>',
				'<div class="ip">{ip}:{porta}</div>',
			]);
		this.template.overwrite(this.el,{
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
		Ext.get('msg').setVisible(false);
		try {
			caMediaPlayer.toSetPositionAndSize(650,70,300,200);
			caMediaPlayer.toPlayerInfo( 1 );
		}catch(e){}
	},
	hide : function(){
		this.el.setVisible(false);
		Ext.get('msg').setVisible(true);
		try {
			caMediaPlayer.toSetFullScreen();
			Cianet.ux.PlayerState.fullscreen = true;
			caMediaPlayer.toPlayerInfo( 0 );
		}catch(e){}
	}
}//END: Cianet.ux.mediainfo = {




















// Player status
Cianet.ux.PlayerState = {
	fullscreen:true,
	plaing:false,
	info:false,
	filtering:false,
	osd:false
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
		debug('movie.stop');
		try {
			caMediaPlayer.toStop();
			caMediaPlayer.toExit();
		} catch (e) {}
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
		debug('movie.repeat');
		try {
			if( caMediaPlayer.toGetRepeatMode() )
				caMediaPlayer.toSetRepeatMode( false );
			else
				caMediaPlayer.toSetRepeatMode( true );
		} catch (e){}
		this.fireEvent('repeat');
	},
	info : function(){
		debug('movie.info');
		try {
			var info = caMediaPlayer.toGetStreamInfo();
			debug('info',info);
		} catch (e){}
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
		this.el.remove();
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
		a.moveTo(800, 650, anim);
	else
		a.moveTo(0,0, anim);
};//END: function anime() {


function loadMedia(){
	var selected = Cianet.ux.movies.getSelected();
	if (selected != undefined)
		var numero = selected.numero;
	else
		var numero = -1;
	Ext.Ajax.request({
		url : 'canal_list/',
		failure: function(resp,obj) {
			debug('Falhou',resp);
			//alert('Erro na comunicação com o servidor');
		},
		// Handler[success]
		success : function(resp, obj) {
			Cianet.ux.movies.removeAll();
			//debug('Canais',Cianet.ux.movies);
			resObject = Ext.util.JSON.decode(resp.responseText);
			var movies = Ext.get('movies');
			vod_playlist = resObject.data;
			for ( var i = 0; i < vod_playlist.length; i++) {
				var movie = new Cianet.ux.Movie(vod_playlist[i]);

				// Event[play]
				movie.on('play',function(){
					Ext.fly('msg').update('Rodando '+this.nome);
					Ext.get('movies').hide();
					Cianet.ux.mediainfo.hide();
				},movie);

				// Event[stop]
				movie.on('stop',function(){
					Ext.fly('msg').update('Parado '+this.nome);
					Ext.get('movies').show();
					Cianet.ux.mediainfo.hide();
				},movie);

				// Event[select]
				movie.on('select',function(){
					// Ajusta o scroll da pagina
					var scroll = movies.getScroll();
					var y = this.el.getY();
					movies.scrollTo('top',(y+scroll.top-300));
					Cianet.ux.mediainfo.setMovie(this);
				},movie);

				// Event[info]
				movie.on('info',function(){
					Cianet.ux.mediainfo.setMovie(this);
					//Cianet.ux.mediainfo.setMovieName(this.name);
					//Cianet.ux.mediainfo.setMovieName(this.name);
					//Cianet.ux.mediainfo.setMovieHost(this.ip);
					//Cianet.ux.mediainfo.setMoviePort(this.porta);
					//Cianet.ux.mediainfo.setMovieId(this.id);
					Cianet.ux.mediainfo.toogle();
				},movie);

				// Event[fullscreen]
				movie.on('fullscreen',function(){
					if (Cianet.ux.PlayerState.fullscreen == true){
						Cianet.ux.mediainfo.hide();
					}else {
						Cianet.ux.mediainfo.show();
					}
				},movie);

				Cianet.ux.movies.push(movie);
				if (numero == movie.numero)
					movie.select();
			}
			if (numero == -1)
				Cianet.ux.movies[0].select();
			//Cianet.ux.mediainfo.setMovie(Cianet.ux.movies[0]);
			//Cianet.ux.mediainfo.toogle();
			//Cianet.ux.mediainfo.toogle();
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
		alert(e);
	}
}


function osd()
{
	try {
		//toSetHolePositionAndSize( int idx, int x, int y, int w, int h );	// to create hole
		//toDelHole( int idx );	// to delete hole
		//alert('Criando hole ----------------------------------');
		//caMediaPlayer.toSetHolePositionAndSize( 0 , 10 , 10 , 800 , 600 );
		//toSetHolePostionAndSize
		//toSetHolePositionAndSize
		if (Cianet.ux.PlayerState.osd){
			Cianet.ux.PlayerState.osd = false;
			var o = caMediaPlayer.toSetHolePostionAndSize( 0 , 100 , 100 , 300 , 300 );
		}else {
			Cianet.ux.PlayerState.osd = true;
			var o = caMediaPlayer.toDelHole( 0 );
		}
	}catch(e){
		alert(e);
	}
}

var atualizador_canal = {
	run:function(){
		Ext.Ajax.request({
			url : 'canal_update/',
			// Handler[failure]
			failure: function(resp,obj) {
				debug('Falhou',resp);
				//alert('Erro na comunicação com o servidor');
			},
			// Handler[success]
			success : function(resp, obj) {
				resObject = Ext.util.JSON.decode(resp.responseText);
				var atualizado = new Date(resObject.atualizado);
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
	interval:10*1000
};

Ext.onReady(function() {
	var DOC = Ext.get(document);
	Cianet.ux.mediainfo.setEl(Ext.get('mediainfo'));
	Cianet.ux.mediainfo.hide();
	showAnim = {
		duration : 4
	};
	// Call load media list from webservice
	Ext.TaskMgr.start(atualizador_canal);
	//loadMedia();
	// Handler[keypress]
	DOC.on('keypress', function(event, opt) {
		var key = event.getKey();
		//Ext.fly('an').update('KEY:'+key);
		//debug('KEY= '+key+' ');

		if ( (Browser.KEY.N_0) <= key && Browser.KEY.N_9 >= key){
			debug('Numeric',event,opt);
		}

		switch (key) {
		case Browser.KEY.a:
			anime();
			//Cianet.ux.movies.showAll();
			break;
		case Browser.KEY.n:
			getIP();
			break;
		case Browser.KEY.o:
			osd();
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
			var movie = Cianet.ux.movies.selectNext();
			movie.play();
			movie.play();
			break;
		case Browser.KEY.LEFT:
			var running = Cianet.ux.movies.getSelected();
			running.stop();
			var movie = Cianet.ux.movies.selectPrevius();
			movie.play();
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


