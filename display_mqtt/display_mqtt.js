
var shop_id_default = "shop1"

var hostname = "broker.hivemq.com";
var port = 8000;
var clientId = "Display";
clientId += new Date().getUTCMilliseconds();;

mqttClient = new Paho.MQTT.Client(hostname, port, clientId);
mqttClient.onMessageArrived =  MessageArrived;
mqttClient.onConnectionLost = ConnectionLost;
Connect();

/*Initiates a connection to the MQTT broker*/
function Connect(){
	mqttClient.connect({
		onSuccess: Connected,
		onFailure: ConnectionFailed,
		keepAliveInterval: 10
	});
}

function GetTopic(){
	var shop_id = shop_id_default;
	if(window.location.hash) {
		shop_id = window.location.hash.substr(1);
	  } 
	return 'de/smartcity/2020/mymall/shops/'+shop_id+'/actuators/display/action';
}

/*Callback for successful MQTT connection */
function Connected() {
  console.log("Connected");
  console.log("Subscribing to topic: "+GetTopic());
  mqttClient.subscribe(GetTopic());
}

/*Callback for failed connection*/
function ConnectionFailed(res) {
	console.log("Connect failed:" + res.errorMessage);
}

/*Callback for lost connection*/
function ConnectionLost(res) {
  if (res.errorCode != 0) {
	console.log("Connection lost:" + res.errorMessage);
	//Connect();
  }
}

/*Callback for incoming message processing */
function MessageArrived(message) {
	console.log(message.destinationName +" : " + message.payloadString);
	var payload = JSON.parse(message.payloadString)
	document.getElementById("message").innerHTML = payload.action.message;
	document.getElementById("symbol").src = payload.action.symbol;
	document.getElementById("outer").style.backgroundColor = payload.action.color;
}



