/**
 *
 */

function sleep(milliseconds) {
	var start = new Date().getTime();
	for ( var i = 0; i < 1e7; i++) {
		if ((new Date().getTime() - start) > milliseconds) {
			break;
		}
	}
}

function debug() {
	// Firefox firebug
	try {
		console.debug(arguments);
	} catch (e) {}
	// return;
	// Cameo console
	try {
		// caFileBrowseObj.Sayhello("DEBUG:T:"+new Date());
		for ( var i = 0; i < arguments.length; i++)
			caFileBrowseObj.Sayhello("DEBUG: "
					+ Ext.util.JSON.encode(arguments[i]));
	} catch (e) {}
};

function debugError() {
	debug('ERRO',arguments);
}
// Debug inicial
debug('Carregado o debug');
