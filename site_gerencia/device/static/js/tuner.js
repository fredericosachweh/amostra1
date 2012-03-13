/**
 * @author Eduardo Vieira
 */

function populate_selects(sat)
{
	django.jQuery('select#id_trans').attr("disabled", "disabled");
	django.jQuery('select#id_chan').attr("disabled", "disabled");
	// Fill the transponders <select>
	var query =  "/tv/dvbinfo/transponders/?sat=" + sat;
	if (django.jQuery('input#id_fta').attr('checked')) query += '&fta=1';
	django.jQuery.getJSON(query, function(data) {
		django.jQuery('select#id_trans').empty();
        django.jQuery.each(data, function(key, value) {
        	var option = '<option value="' + value.pk + '">';
        	if (value.fields.name) option += value.fields.name + ' - ';
        	option += value.fields.frequency.toString() + ' '; 
        	option += value.fields.polarization + ' ';
        	option += value.fields.symbol_rate.toString();
        	option += '</option>';
        	django.jQuery('select#id_trans').append(option);
        });
        django.jQuery('select#id_trans').removeAttr("disabled");
    });
    // Also fill the channels <select> field
    query =  "/tv/dvbinfo/channels/?sat=" + sat;
	if (django.jQuery('input#id_fta').attr('checked')) query += '&fta=1';
    django.jQuery.getJSON(query, function(data) {
		django.jQuery('select#id_chan').empty();
        django.jQuery.each(data, function(key, value) {
        	var option = '<option value="' + value.pk + '">' + value.fields.name + '</option>'; 
        	django.jQuery('select#id_chan').append(option);
        });
        django.jQuery('select#id_chan').removeAttr("disabled");
    });
}

function fill_form(data)
{
	var json = data[0]
	django.jQuery('input#id_frequency').val(json.fields.frequency);
	django.jQuery('input#id_symbol_rate').val(json.fields.symbol_rate);
	django.jQuery('select#id_modulation').val(json.fields.modulation);
	django.jQuery('select#id_polarization').val(json.fields.polarization);
}

function transponder_fill_form(transponder)
{
	var query = "/tv/dvbinfo/transponders/?trans=" + transponder;
	django.jQuery.getJSON(query, fill_form);
}

function channel_fill_form(channel)
{
	var query = "/tv/dvbinfo/transponders/?chan=" + channel;
	django.jQuery.getJSON(query, fill_form);
}