var shopIdsGraph = ['shop1', 'shop2', 'shop3', 'shop4'];
var shopsGraph = {};

function init() {
    shopIdsGraph.forEach(function (shopId) {
        var shop = {
            sensors_raw: {ble: {}, cam: {}, wifi: {}},
            sensors: {ble: null, cam: null, wifi: null},
            people: null,
            actuators: {display: null}
        };

        shopsGraph[shopId] = shop;
    })
}

init();

var hostname = hostname || "broker.hivemq.com";
var port = port || 8000;
var clientIdGraph = "graph";
clientIdGraph += new Date().getUTCMilliseconds();

mqttClientGraph = new Paho.MQTT.Client(hostname, port, clientIdGraph);
mqttClientGraph.onMessageArrived = MessageArrivedGraph;
mqttClientGraph.onConnectionLost = ConnectionLostGraph;
ConnectGraph();

/*Initiates a connection to the MQTT broker*/
function ConnectGraph() {
    mqttClientGraph.connect({
        onSuccess: ConnectedGraph,
        onFailure: ConnectionFailedGraph,
        keepAliveInterval: 10
    });
}

/*Callback for successful MQTT connection */
function ConnectedGraph() {
    console.log("Connected");
    mqttClientGraph.subscribe('de/smartcity/2020/mymall/shops/+/sensors/#');
    mqttClientGraph.subscribe('de/smartcity/2020/mymall/shops/+/sensors_raw/#');
    mqttClientGraph.subscribe('de/smartcity/2020/mymall/shops/+/people/count');
    mqttClientGraph.subscribe('de/smartcity/2020/mymall/shops/+/actuators/display/action');
    document.getElementById('statusGraph').innerHTML = "MQTT connected!";
    document.getElementById('statusGraph').style.backgroundColor = 'greenyellow';
}

/*Callback for failed connection*/
function ConnectionFailedGraph(res) {
    console.log("Connect failed:" + res.errorMessage);
}

/*Callback for lost connection*/
function ConnectionLostGraph(res) {
    if (res.errorCode != 0) {
        console.log("Connection lost:" + res.errorMessage);
        //Connect();
        document.getElementById('statusGraph').innerHTML = "MQTT connection lost!  <button type=\"button\" onclick=\"ConnectGraph()\">reconnect</button>";
        document.getElementById('statusGraph').style.backgroundColor = 'red';
    }
}

const wifiVirtRegex = /^de\/smartcity\/2020\/mymall\/shops\/[^\/]+\/sensors\/wifi\/list/;
const bleVirtRegex = /^de\/smartcity\/2020\/mymall\/shops\/[^\/]+\/sensors\/ble\/list/;
const camVirtRegex = /^de\/smartcity\/2020\/mymall\/shops\/[^\/]+\/sensors\/cam\/count/;
const camRawRegex = /^de\/smartcity\/2020\/mymall\/shops\/[^\/]+\/sensors_raw\/cam\/[^\/]+\/count/;
const bleRawRegex = /^de\/smartcity\/2020\/mymall\/shops\/[^\/]+\/sensors_raw\/ble\/[^\/]+\/list/;
const wifiRawRegex = /^de\/smartcity\/2020\/mymall\/shops\/[^\/]+\/sensors_raw\/wifi\/[^\/]+\/list/;
const peopleTRegex = /^de\/smartcity\/2020\/mymall\/shops\/[^\/]+\/people\/count/;
const displayRegex = /^de\/smartcity\/2020\/mymall\/shops\/[^\/]+\/actuators\/display\/action/;

/*Callback for incoming message processing */
function MessageArrivedGraph(message) {
    console.log(message.destinationName + " : " + message.payloadString);
    //addTableElement(message.destinationName, message.payloadString);

    var count = -1;
    var payload = JSON.parse(message.payloadString);
    var shopId = payload.shop_id;

    var result = {
        topic: message.destinationName,
        payload: message.payloadString,
        timestamp: Date.now(),
        retained: message.retained
    };

    if (message.destinationName.match(displayRegex)) {
        result['level'] = 3;
        result['name'] = payload.action.message;
        result['color'] = payload.action.color;
        result['image'] = payload.action.symbol;
        result['id'] = 'display ' + shopId;
        result['title'] = 'display<br>' + shopId;

        if (compareWithoutTime(shopsGraph[shopId]['actuators']['display'], result)) {
            return;
        }

        shopsGraph[shopId]['actuators']['display'] = result;
    } else {
        var sensorType = payload.sensor_type;
        var sensorName = 'virtual ' + sensorType + '<br>' + shopId;
        if (payload.sensor_id != null) {
            sensorName = sensorType + '<br>' + payload.sensor_id;
        }
        result['title'] = sensorName;
        result['id'] = sensorName;

        if (message.destinationName.match(peopleTRegex)) {
            result['level'] = 2;
            //people message
            result['count'] = payload.count;
            result['color'] = '#BEB8AF';
            result['name'] = 'Count: ' + result['count'];
            if (compareWithoutTime(shopsGraph[shopId]['people'], result)) {
                return;
            }
            shopsGraph[shopId]['people'] = result;
        } else if (message.destinationName.match(wifiVirtRegex)) {
            result['level'] = 1;
            //virt wifi message
            result['count'] = Object.keys(payload.clients).length;
            result['color'] = '#FCF4B7';
            result['name'] = 'Count: ' + result['count'];
            if (compareWithoutTime(shopsGraph[shopId]['sensors']['wifi'], result)) {
                return;
            }
            shopsGraph[shopId]['sensors']['wifi'] = result;
            if (payload.delete === true) {
                shopsGraph[shopId]['sensors']['wifi'] = null;
            }

        } else if (message.destinationName.match(bleVirtRegex)) {
            result['level'] = 1;
            result['count'] = payload.clients.length;
            result['color'] = '#f3c4ff';
            result['name'] = 'Count: ' + result['count'];
            if (compareWithoutTime(shopsGraph[shopId]['sensors']['ble'], result)) {
                return;
            }
            shopsGraph[shopId]['sensors']['ble'] = result;
            if (payload.delete === true) {
                shopsGraph[shopId]['sensors']['ble'] = null;
            }

        } else if (message.destinationName.match(camVirtRegex)) {
            result['level'] = 1;
            result['count'] = payload.count;
            result['color'] = '#a7ecfd';
            result['name'] = 'Count: ' + result['count'];
            if (compareWithoutTime(shopsGraph[shopId]['sensors']['cam'], result)) {
                return;
            }
            shopsGraph[shopId]['sensors']['cam'] = result;
            if (payload.delete === true) {
                shopsGraph[shopId]['sensors']['cam'] = null;
            }

        } else if (message.destinationName.match(camRawRegex)) {
            result['level'] = 0;
            result['count'] = payload.count;
            result['color'] = '#DEF3FD';
            result['name'] = 'Count: ' + result['count'];
            result['emptyMsg'] = generateMessagesEmpty(shopId, sensorType, payload.sensor_id);
            if (compareWithoutTime(shopsGraph[shopId]['sensors_raw']['cam'][sensorName], result)) {
                return;
            }
            shopsGraph[shopId]['sensors_raw']['cam'][sensorName] = result;
            if (payload.delete === true) {
                delete shopsGraph[shopId]['sensors_raw']['cam'][sensorName]
            }

        } else if (message.destinationName.match(bleRawRegex)) {
            result['level'] = 0;
            result['count'] = payload.clients.length;
            result['color'] = '#F0DEFD';
            result['name'] = 'Count: ' + result['count'];
            result['emptyMsg'] = generateMessagesEmpty(shopId, sensorType, payload.sensor_id);
            if (compareWithoutTime(shopsGraph[shopId]['sensors_raw']['ble'][sensorName], result)) {
                return;
            }
            shopsGraph[shopId]['sensors_raw']['ble'][sensorName] = result;
            if (payload.delete === true) {
                delete shopsGraph[shopId]['sensors_raw']['ble'][sensorName]
            }

        } else if (message.destinationName.match(wifiRawRegex)) {
            // raw wifi
            result['level'] = 0;
            result['count'] = Object.keys(payload.clients).length;
            result['color'] = '#FCF7DE';
            result['name'] = 'Count: ' + result['count'];
            result['emptyMsg'] = generateMessagesEmpty(shopId, sensorType, payload.sensor_id);
            if (compareWithoutTime(shopsGraph[shopId]['sensors_raw']['wifi'][sensorName], result)) {
                return;
            }
            shopsGraph[shopId]['sensors_raw']['wifi'][sensorName] = result;
            if (payload.delete === true) {
                delete shopsGraph[shopId]['sensors_raw']['wifi'][sensorName]
            }

        } else {
            console.log("Uncatched topic: " + message.destinationName);
            return
        }
    }

    updateShopGraph(shopId);

}

function generateMessagesEmpty(shopId, sensorType, sensorId) {
    var namespace = 'de/smartcity/2020/mymall';
    var value = 0;
    console.log(shopId, sensorType, value);


    var id = sensorId;

    var topics = {
        ble: namespace + '/shops/' + shopId + '/sensors_raw/' + sensorType + '/' + sensorId + '/list',
        cam: namespace + '/shops/' + shopId + '/sensors_raw/' + sensorType + '/' + sensorId + '/count',
        wifi: namespace + '/shops/' + shopId + '/sensors_raw/' + sensorType + '/' + sensorId + '/list'
    };

    var topic = topics[sensorType];
    var payload = {
        sensor_type: sensorType,
        sensor_id: id, shop_id: shopId,
        delete: true
    };
    if (sensorType === 'ble') {
        var clients = Array.from(Array(value).keys()).map(String);
        payload.clients = clients;
    } else if (sensorType === 'cam') {
        payload.count = value;
    } else if (sensorType === 'wifi') {
        var clientsArray = Array.from(Array(value).keys()).map(String);
        var clients = {};
        clientsArray.forEach(function (val) {
            clients['ip' + val] = 'hmac' + val;
        });
        payload.clients = clients;
    } else {
        console.log('Unreachable case!! type: ', sensorType);
    }
    var results = [];
    var message = new Paho.MQTT.Message(JSON.stringify(payload));
    message.destinationName = topic;
    results.push(message);
    if (sensorType === 'cam') {
        return results;
    }

    topics = {
        ble: namespace + '/shops/' + shopId + '/sensors_raw/' + sensorType + '/' + sensorId + '/count',
        cam: namespace + '/shops/' + shopId + '/sensors_raw/' + sensorType + '/' + sensorId + '/count',
        wifi: namespace + '/shops/' + shopId + '/sensors_raw/' + sensorType + '/' + sensorId + '/count'
    };


    topic = topics[sensorType];
    payload = {
        sensor_type: sensorType,
        sensor_id: id, shop_id: shopId,
        delete: true
    };

    if (sensorType === 'ble') {
        var clients = Array.from(Array(value).keys()).map(String);
        payload.count = clients.length;
    } else if (sensorType === 'wifi') {
        var clientsArray = Array.from(Array(value).keys()).map(String);
        payload.count = clientsArray.length;
    } else {
        console.log("Should never happen");
        return results;
    }

    message = new Paho.MQTT.Message(JSON.stringify(payload));
    message.destinationName = topic;
    results.push(message);

    return results;
}

function compareWithoutTime(reference, value) {
    var actualValue = Object.assign({}, reference, {timestamp: undefined, emptyMsg: undefined});
    var croppedValue = Object.assign({}, value, {timestamp: undefined, emptyMsg: undefined});
    // Compare without timestamp
    if (JSON.stringify(actualValue) === JSON.stringify(croppedValue)) {
        return true;
    }
    return false;
}

function updateShopGraph(shopId) {
    var shop = shopsGraph[shopId];
    //console.log(shop);

    var cData = [];
    var cNodes = [];

    if (shop['actuators']['display'] != null) {
        cNodes.push(shop['actuators']['display']);
    }

    if (shop['people'] != null) {
        cNodes.push(shop['people']);
        if (shop['actuators']['display'] != null) {
            cData.push([shop['people'].id, shop['actuators']['display'].id]);
        }
    }
    var sensorTypeCount = 0;
    Object.keys(shop['sensors']).forEach(function (virtSensorType) {
        var virtSensor = shop['sensors'][virtSensorType];
        if (virtSensor != null) {
            sensorTypeCount++;
            cNodes.push(virtSensor);
            if (shop['people'] != null) {
                cData.push([virtSensor.id, shop['people'].id]);
            }
        }
    });
    var sensorCount = 0;
    Object.keys(shop['sensors_raw']).forEach(function (sensorsType) {
        var sensors = shop['sensors_raw'][sensorsType];
        Object.keys(sensors).forEach(function (sensorId) {
            var sensor = sensors[sensorId];
            sensorCount++;
            if (sensor != null) {
                cNodes.push(sensor);
                if (shop['sensors'][sensorsType] != null) {
                    cData.push([sensor.id, shop['sensors'][sensorsType].id]);
                }
            }
        })
    });

    //console.log(cData);
    //console.log(cNodes);

    var options = {
        chart: {
            height: Math.max(Math.max(sensorCount, sensorTypeCount), 1) * 85 + 50,
            // width: 600,
            inverted: false,
            renderTo: 'c' + shopId,
            animation: false
        },

        title: {
            text: ''
        },

        plotOptions: {
            series: {
                nodeWidth: '22%',
                animation: 0
            }
        },

        series: [{
            type: 'organization',
            name: 'Highsoft',
            keys: ['from', 'to'],
            data: cData,
            nodes: cNodes,
            colorByPoint: false,
            borderColor: 'white',
            events: {
                click: function (event) {
                    if (event.shiftKey && event.point.emptyMsg != null) {
                        // override with zero values
                        event.point.emptyMsg.forEach(function (msg) {
                            msg.retained = event.point.retained;
                            mqttClientGraph.send(msg);
                        });
                        // delete message
                        event.point.emptyMsg.forEach(function (msg) {
                            msg.retained = true;
                            msg.payload = "";
                            mqttClientGraph.send(msg);
                        });
                    }

                }
            },
            dataLabels: {
                color: 'black',
                nodeFormatter: function () {
                    // Call the default renderer
                    var html = Highcharts.defaultOptions
                        .plotOptions
                        .organization
                        .dataLabels
                        .nodeFormatter
                        .call(this);

                    // Do some modification
                    if (this.point.timestamp + 3000 > Date.now()) {
                        html = html.replace(
                            '<div ',
                            '<div class="newValGraph" '
                        );
                    }
                    //console.log(html);
                    return html;
                }
            }
        }],

        tooltip: {
            outside: true,
            formatter: function () {
                return this.point.topic + '<br>' + this.point.payload;
            }
        }
    };

    var charts = Highcharts.chart('c' + shopId, options);


}

/*
var chart = Highcharts.chart('container', {

    chart: {
        height: 600,
        inverted: false,
        renderTo: 'container',
        animation: false
    },

    title: {
        text: 'Carnivora Phylogeny'
    },

    plotOptions: {
        series: {
            nodeWidth: '22%',
            animation: 0
        }
    },

    series: [{
        type: 'organization',
        name: 'Highsoft',
        keys: ['to', 'from'],
        data: [
            ['Carnivora', 'Felidae'],
            ['Carnivora', 'Mustelidae'],
            ['Carnivora', 'Canidae'],
            ['Felidae', 'Panthera'],
            ['Mustelidae', 'Taxidea'],
            ['Mustelidae', 'Lutra'],
            ['Panthera', 'Panthera pardus'],
            ['Taxidea', 'Taxidea taxus'],
            ['Lutra', 'Lutra lutra'],
            ['Canidae', 'Canis'],
            ['Canis', 'Canis latrans'],
            ['Canis', 'Canis lupus']
        ],
        levels: [{
            level: 0,
            color: '#DEDDCF',
            borderLine: 10,
            dataLabels: {
                color: 'black'
            }
        }, {
            level: 1,
            color: '#DEDDCF',
            dataLabels: {
                color: 'black'
            },
            height: 25
        }, {
            level: 2,
            color: '#DEDDCF',
            dataLabels: {
                color: 'black'
            },
        }, {
            level: 3,
            dataLabels: {
                color: 'black'
            },
        }],
        nodes: [{
            id: 'Carnivora',
            title: null,
            name: 'Carnivora',
            info: "Carnivora is a diverse scrotiferan order that includes over 280 species of placental mammals."
        }, {
            id: 'Felidae',
            title: null,
            name: 'Felidae',
            color: "#fcc657",
            info: "Felidae is a family of mammals in the order Carnivora, <br>colloquially referred to as cats, and constitute a clade."
        }, {
            id: 'Panthera',
            title: null,
            name: 'Panthera',
            color: "#fcc657",
            info: "Panthera"
        }, {
            id: 'Panthera pardus',
            title: null,
            name: 'Panthera pardus',
            color: "#fcc657",
            image: "https://raw.githubusercontent.com/mekhatria/demo_highcharts/master/panthera.png",
            info: "Panthera is a genus within the Felidae family <br>that was named and described by Lorenz Oken in 1816 <br>who placed all the spotted cats in this group."
        }, {
            id: 'Mustelidae',
            title: null,
            name: 'Mustelidae',
            color: "#C4B1A0",
            info: "The Mustelidae are a family of carnivorous mammals,<br> including weasels, badgers, otters, ferrets, martens, mink, and wolverines, among others."
        }, {
            id: 'Taxidea',
            title: null,
            name: 'Taxidea',
            color: "#C4B1A0",
            info: "Taxidea"
        }, {
            id: 'Lutra',
            color: "#C4B1A0",
            info: "Lutra"
        }, {
            id: 'Taxidea taxus',
            name: 'Taxidea taxus',
            color: "#C4B1A0",
            image: "https://raw.githubusercontent.com/mekhatria/demo_highcharts/master/taxideaTaxus.png",
            info: "Taxidea taxus is a North American badger, <br>somewhat similar in appearance to the European badger, <br>although not closely related. <br>It is found in the western and central United States, <br>northern Mexico, and south-central Canada to certain areas of southwestern British Columbia."
        }, {
            id: 'Lutra lutra',
            name: 'Lutra lutra',
            color: "#C4B1A0",
            image: "https://raw.githubusercontent.com/mekhatria/demo_highcharts/master/lutra.png",
            info: "Lutra is a semiaquatic mammal native to Eurasia. <br>The most widely distributed member of the otter subfamily (Lutrinae) of the weasel family (Mustelidae), <br>it is found in the waterways and coasts of Europe, many parts of Asia, <br>and parts of northern Africa."
        }, {
            id: 'Canidae',
            name: 'Canidae',
            color: "#B0ACA2",
            info: "The biological family Canidae is a lineage of carnivorans <br>that includes domestic dogs, wolves, coyotes, foxes, jackals, dingoes, <br>and many other extant and extinct dog-like mammals. "
        }, {
            id: 'Canis',
            name: 'Canis',
            color: "#B0ACA2",
            info: "Canis"
        }, {
            id: 'Canis latrans',
            name: 'Canis latrans',
            color: "#B0ACA2",
            image: "https://raw.githubusercontent.com/mekhatria/demo_highcharts/master/canisLatrans.png",
            info: "Canis latrans, is a canine native to North America.<br> It is smaller than its close relative, the gray wolf, and <br>slightly smaller than the closely related eastern wolf and red wolf."
        }, {
            id: 'Canis lupus',
            name: 'Canis lupus',
            color: "#B0ACA2",
            image: "https://raw.githubusercontent.com/mekhatria/demo_highcharts/master/canisLupus.png",
            info: "Canis lupus is a canine native to the wilderness and remote areas of Eurasia and North America. <br>It is the largest extant member of its family, with males averaging 43–45 kg (95–99 lb) <br>and females 36–38.5 kg (79–85 lb)."
        }],
        colorByPoint: false,
        borderColor: 'white'
    }],

    tooltip: {
        outside: true,
        formatter: function () {
            return this.point.info;
        }
    },

    exporting: {
        allowHTML: true,
        sourceWidth: 800,
        sourceHeight: 600
    }
});*/


