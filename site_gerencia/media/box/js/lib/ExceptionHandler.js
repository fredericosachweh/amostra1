Ext.ns('Cianet.lib');

Cianet.lib.log = function(message, stack){
	if (!this.logging){
		this.logging = false;
		Ext.Ajax.request({
			url:'remote_log/',
			method: 'post',
			params: {
				body:message,
				stack:stack
			},
			success: function(transport){
				this.logging = false;
			}
		});
	}
};

function handleException(exception){
	if (typeof exception == 'string') exception = new Error(exception);
	if (exception.name == 'NS_ERROR_NOT_AVAILABLE') return;
	var fullMessage = '';
	var uri = '';
	var stack = '';
	var line = '';

	try{
		fullMessage = exception.name + ': ' + exception.message;
		uri = exception.fileName;
		stack = exception.stack;
		line = exception.lineNumber;
	} catch (e){}

	fullMessage += ' em ' + uri + ": linha " + line;
	try{
		console.warn(fullMessage);
		console.warn(stack);
	} catch(e){}
	Cianet.lib.log(fullMessage, stack);
	//alert('Ocorreu um erro processando requisição:\n'+fullMessage);
};

// Register global error handler
window.onerror=function(message, uri, line){
	//if ( message.match("chrome://")) return false;
	var fullMessage = message + "\n em " + uri + ": linha " + line;
	Cianet.lib.log(fullMessage);
	// Let the browser take it from here
	return false;
	// Interromper
	//return true;
};

Ext.onReady(function(){

});


