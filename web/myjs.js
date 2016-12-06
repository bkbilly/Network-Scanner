var socket = io();
var sensor = '<div class="hostdiv" id="hostdiv{mac}" style="{cssDiv}">\
	<div class="hostname" id="hostname{mac}" onclick="changeName(this, \'{mac}\')">{hostname}</div>\
	<div class="hostip">{hostip}</div>\
	<div class="hostmac">{mac}</div>\
</div>'

$( document ).ready(function() {
	var modal = document.getElementById('myModal');
	var span = document.getElementsByClassName("close")[0];
	span.onclick = function() {
		closeConfigWindow();
	}
	window.onclick = function(event) {
		if (event.target == modal) {
			closeConfigWindow();
		}
	}

	startAgain();

	socket.on('refresh_devices', function(msg){
		startAgain();
	});
});

function startAgain(){
	$("#sensors").empty();
	$.getJSON("getDevices.json").done(function(data){
		console.log(data);
		$.each(data, function(i, item){
			var tmpsensor = sensor
			btnColour = (item.state === "up" ? "green" : "red");
			shadowBtnColour = "box-shadow: inset 0px 30px 40px -20px " + btnColour + ";"
			tmpsensor = tmpsensor.replace(/\{mac\}/g, item.mac)
			tmpsensor = tmpsensor.replace(/\{hostname\}/g, item.name)
			tmpsensor = tmpsensor.replace(/\{hostip\}/g, item.ip)
			tmpsensor = tmpsensor.replace(/\{cssDiv\}/g, shadowBtnColour)
			$(tmpsensor).appendTo("#sensors");
		});
	});
}


function changeName(div, mac){
	$("#okButton").attr("onclick","saveConfigSettings('"+mac+"')");
	currentName = div.innerHTML;
	$("#inputName").val(currentName);
	$("#inputName").show();
	$("#myModal").show();
}

function saveConfigSettings(mac){
	var newname = $("#inputName").val();
	socket.emit('changeName', {"mac": mac, "name": newname});
	closeConfigWindow();
}

function openConfigWindow(){
    $("#myModal").show();
}

function closeConfigWindow(){
	$("#myModal").hide();
}