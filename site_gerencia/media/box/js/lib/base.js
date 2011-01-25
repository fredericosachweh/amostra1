/**
 *
 * @param milliseconds
 */
function sleep(milliseconds) {
	var start = new Date().getTime();
	for ( var i = 0; i < 1e7; i++) {
		if ((new Date().getTime() - start) > milliseconds) {
			break;
		}
	}
}
/**
 * Garbage collector
 * @param d
 */
function purge(d) {
    var a = d.attributes, i, l, n;
    if (a) {
        l = a.length;
        for (i = 0; i < l; i += 1) {
            n = a[i].name;
            if (typeof d[n] === 'function') {
                d[n] = null;
            }
        }
    }
    a = d.childNodes;
    if (a) {
        l = a.length;
        for (i = 0; i < l; i += 1) {
            purge(d.childNodes[i]);
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
