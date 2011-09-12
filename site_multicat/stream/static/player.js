
$(document).ready(function(){
	//alert('Aqui!!!!');
	var p1 = $('#stream_id_1');
	console.debug(p1);
	console.debug($(document));
});

function callPlay(streamId){
	window.location.href = '/process/play/'+streamId+'/';
	//$.ajax('/process/play/'+streamId+'/');
}

function callStop(streamId){
	window.location.href = '/process/stop/'+streamId+'/';
	//$.ajax('/process/stop/'+streamId+'/');
}
