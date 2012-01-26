
function callPlay(streamId){
	window.location.href = '/process/play/'+streamId+'/';
	//$.ajax('/process/play/'+streamId+'/');
}

function callStop(streamId){
	window.location.href = '/process/stop/'+streamId+'/';
	//$.ajax('/process/stop/'+streamId+'/');
}



$(document).ready(function(){
	var selector_import = "a#link-to-import-data";
	var selector_delete = "a#link-to-delete-data";
	var patt=/arquivo_epg\/(\d*)\//;
	var pk = patt.exec( document.location.href )[1];
	if ( pk ) {
		$("a#link-to-import-data").click(function(){
			import_epg( pk );
		});
		$("a#link-to-delete-data").click(function(){
			delete_epg( pk );
		});
	}
});

function import_epg_success( data ){
	alert( data );
}

function import_epg( pk ){
	var resp = $.ajax({
		url: '/tv/epg/import/' + pk + '/',
		dataType: 'json',
		success: import_epg_success
	});
}

function delete_epg( pk ){
	alert( "delete " + pk );
}

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
		url:'/tv/stream/scan_dvb/'+sid+'/',
		dataType: 'json',
		success:scan_dvb_success
		});
}


