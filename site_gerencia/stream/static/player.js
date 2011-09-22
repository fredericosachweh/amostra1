
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
	var sid = $('#id_origem-__prefix__-source').val();
	if (sid) {
		//alert(sid);
		$(selector).append(" (<a class=\"collapse-toggle\" id=\"customcollapser\" href=\"#\"> Buscar </a>)");
		$("#customcollapser").click(function() {
		    //$(selector).parent().toggleClass("collapsed");
		    scan_dvb();
		});
	}
});

function scan_dvb_success(data){
	//alert(data.length);
	$.each(data,function(i,j){
		var prg = j['program'];
		var pid = j['pid'];
		$('#id_origem-'+i+'-channel_program').val(prg);
		$('#id_origem-'+i+'-channel_pid').val(pid);
	});
	if (data.length == 0)
		alert('Não foi localizado nenhum canal!');
	else
		alert('Localizado '+ data.length + ' canais.');
	
}

function scan_dvb(){
	var sid = $('#id_origem-__prefix__-source').val();
	var resp = $.ajax({
<<<<<<< HEAD
		url:'/%sstream/scan_dvb/'+sid+'/',
=======
		url:'/tv/stream/scan_dvb/'+sid+'/',
>>>>>>> 114d48ffce5f025bf5a949967d5427d97b15dd02
		dataType: 'json',
		success:scan_dvb_success
		});
}


