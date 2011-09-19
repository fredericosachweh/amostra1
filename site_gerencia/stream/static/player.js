
function callPlay(streamId){
	window.location.href = '/process/play/'+streamId+'/';
	//$.ajax('/process/play/'+streamId+'/');
}

function callStop(streamId){
	window.location.href = '/process/stop/'+streamId+'/';
	//$.ajax('/process/stop/'+streamId+'/');
}



$(document).ready(function(){
	var selector = "h2:contains('Destinos de fluxo DVB')";
	//$(selector).parent().addClass("collapsed");
	$(selector).append(" (<a class=\"collapse-toggle\" id=\"customcollapser\" href=\"#\"> Buscar </a>)");
	$("#customcollapser").click(function() {
	    $(selector).parent().toggleClass("collapsed");
	    scan_dvb();
	});
});

function scan_dvb_success(data){
	console.debug(data);
	// id_origem-0-channel_program
	// id_origem-0-channel_pid
}

function scan_dvb(){
	var sid = 1;
	var resp = $.ajax({url:'/stream/scan_dvb/'+sid+'/',success:scan_dvb_success});
}


