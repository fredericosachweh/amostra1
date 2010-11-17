Ext.ns('Browser');
// Default PC keyboard
Browser.KEY = {
	N_0:48,
	N_1:49,
	N_2:50,
	N_3:51,
	N_4:52,
	N_5:53,
	N_6:54,
	N_7:55,
	N_8:56,
	N_9:57,
	a:97,
	b:98,
	c:99,
	d:100,
	e:101,
	f:102,
	g:103,
	h:104,
	i:105,
	j:106,
	k:107,
	l:108,
	m:109,
	n:110,
	o:111,
	p:112,
	q:113,
	r:114,
	s:115,
	t:116,
	u:117,
	v:118,
	w:119,
	x:120,
	y:121,
	z:122,
	HOME:36,
	UP: 38,
	RIGHT: 39,
	DOWN: 40,
	LEFT: 37,
	ESC:27,
	INS:45,
	TAB:9,
	SPACE:32
};

//ARROW BOARD (cameo = arora = safari)
Browser.ARORA = {
	HOME:61445
	,UP: 61442
	,RIGHT: 61441
	,DOWN: 61443
	,LEFT: 61440
	,ENTER:14
	//p:67206
};


Ext.onReady(function(){
	if (Ext.isWebKit)
		Ext.apply(Browser.KEY,Browser.ARORA);
	//else
	//	Ext.apply(Browser.KEY,Browser.TESTE);
	//debug('Browser.KEY',Browser.KEY);
	//debug('Browser.ARORA',Browser.ARORA);
	//debug('Browser.TESTE',Browser.TESTE);

});



