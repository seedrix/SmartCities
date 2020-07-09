

var hostname = "broker.hivemq.com";
var port = 8000;
var clientId = "virtualS";
clientId += new Date().getUTCMilliseconds();

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

const namespace = 'de/smartcity/2020/mymall';

var timer = null;

function startV() {
    var strIn = document.getElementById('listField').value;
    var values = JSON.parse(strIn);

    var shopId = document.getElementById('shopIdField').value;
    var shopColumn = document.getElementById(shopId);

    var intervalSec = parseInt(document.getElementById('interval').value)*1000;

    //timer = setInterval(function(){stepV(values, shopColumn, intervalSec) }, intervalSec);
    stepV(values, shopColumn, intervalSec);


}

function stepV(values, shopColumn, intervalSec){
    if (values.length === 0){
        return;
    }
    const value = values.shift();

    timer = setInterval(function(){stepV(values, shopColumn, intervalSec) }, intervalSec);

    const columnIndexs = {ble:1, cam:2, wifi:3};
    var array = value;
    if (! Array.isArray(value)){
     array = [value, value, value];
    }
    console.log('arr: ',array);
    for (var i = 0; i < 3; i++) {

        var column = shopColumn.children[i+1].children[0];
        column.value = array[i];
        updateValue(column);
    }
}

function stopV() {
    clearInterval(timer);
}


function updateValue(field){
    var shopId = field.getAttribute("shop");
    var sensorType = field.getAttribute("sType");
    var value = parseInt(field.value);
    console.log(shopId, sensorType, value);

    ids = {wifi:'wVirt'+shopId,
        ble:'bVirt'+shopId,
        cam:'cVirt'+shopId};

    var id = ids[sensorType];

    topics = {ble: namespace+'/shops/'+shopId+'/sensors_raw/'+sensorType+'/bVirt'+shopId+'/list',
        cam: namespace+'/shops/'+shopId+'/sensors_raw/'+sensorType+'/cVirt'+shopId+'/count',
        wifi: namespace+'/shops/'+shopId+'/sensors_raw/'+sensorType+'/wVirt'+shopId+'/list'};

    var topic = topics[sensorType];
    var payload = {sensor_type: sensorType,
        sensor_id: id, shop_id:shopId};
    if(sensorType === 'ble'){
        var clients = Array.from(Array(value).keys()).map(String);
        payload.clients = clients;
    }else if(sensorType === 'cam'){
        payload.count = value;
    }else if(sensorType === 'wifi'){
        var clientsArray = Array.from(Array(value).keys()).map(String);
        var clients = {};
        clientsArray.forEach(function(val){
            clients['ip'+val] = 'hmac'+val;
    });
        payload.clients = clients;
    }else{
        console.log('Unreachable case!! type: ', sensorType);
    }
    message = new Paho.MQTT.Message(JSON.stringify(payload));
    message.destinationName = topic;
    var success = true;
    try{
        mqttClient.send(message);
    }catch(err){
        if (err) {
            success = false;
            console.log("Error while sending: ", err);
        }
    }
    if (success){
        animatee(field,'updateVal');
        console.log('sent: ',message);
    }else{
        animatee(field,'errorVal');

    }

}

function animatee(element, className) {
    element.classList.remove('errorVal');
    element.classList.remove('updateVal');
    element.classList.remove('newVal');
    element.classList.add(className);
    element.style.webkitAnimation = 'none';
    setTimeout(function() {
        element.style.webkitAnimation = '';
    }, 10);

}


/*Callback for successful MQTT connection */
function Connected() {
    console.log("Connected");
    mqttClient.subscribe('de/smartcity/2020/mymall/shops/+/sensors/+/count');
    mqttClient.subscribe('de/smartcity/2020/mymall/shops/+/people/count');
    document.getElementById('status').innerHTML = "MQTT connected!";
    document.getElementById('status').style.backgroundColor = 'greenyellow';
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
        document.getElementById('status').innerHTML = "MQTT connection lost!  <button type=\"button\" onclick=\"Connect()\">reconnect</button>";
        document.getElementById('status').style.backgroundColor = 'red';
    }
}

/*Callback for incoming message processing */
function MessageArrived(message) {
    console.log(message.destinationName +" : " + message.payloadString);
    var payload = JSON.parse(message.payloadString);
    var shopId = payload.shop_id;
    var sensorType = payload.sensor_type;
    var count = payload.count;

    const columnIndexs = {ble:4, cam:5, wifi:6, people: 7};

    console.log(shopId, sensorType, count, columnIndexs[sensorType]);

    var column = document.getElementById(shopId).children[columnIndexs[sensorType]];
    column.innerHTML = count;
    animatee(column, 'newVal');

}



