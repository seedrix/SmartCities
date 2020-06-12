import paho.mqtt.client as mqtt
import hashlib
import json
import subprocess
import threading

interface = "wlan0"
command_clients = 'cat /var/lib/misc/dnsmasq.leases | grep -E $(iw dev ' + interface + ' station dump | grep -oE "([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}" | paste -sd "|")'
command_mac = 'iw dev ' + interface + ' info | grep -oE "([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}"'


def get_mac():
    process = subprocess.run(command_mac, stdout=subprocess.PIPE, shell=True)
    result = process.stdout.decode('utf-8')
    return 'w' + result.strip()


broker_hostname = "broker.hivemq.com"
broker_port = 1883

intervall_seconds = 30

namespace = 'de/smartcity/2020/mymall'
clients_list_topic = namespace + '/sensors/wifi/' + get_mac() + '/list'
clients_count_topic = namespace + '/sensors/wifi/' + get_mac() + '/count'

retain_messages = True


def get_connected_clients():
    process = subprocess.run(command_clients, stdout=subprocess.PIPE, shell=True)
    result = process.stdout.decode('utf-8')
    lines = result.splitlines()
    clients = {}
    for line in lines:
        split_line = line.split()
        ip = split_line[2]
        mac = split_line[1]
        name = ''
        if len(split_line) > 3:
            name = split_line[3]
        clients[ip] = {'mac': mac, 'name': name}
    return clients


def generate_client_list_payload(client_dict):
    result = {}
    for ip, client in client_dict.items():
        result[ip] = hashlib.sha224(client['mac'].encode()).hexdigest()
    return {'clients': result}


def publish_data():
    clients = get_connected_clients()
    print(f"Connected clients ({len(clients)}): {clients}")
    mqclient.publish(clients_count_topic, payload=generate_payload({'count': len(clients)}), retain=retain_messages)
    mqclient.publish(clients_list_topic, payload=generate_payload(generate_client_list_payload(clients)),
                     retain=retain_messages)
    print("published data")


def generate_payload(data):
    payload = {'sensor_id': get_mac(), 'sensor_type': 'wifi'}
    payload.update(data)
    print(payload)
    return json.dumps(payload)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print(f"Using the following topics to publish data:\n\t{clients_count_topic}\n\t{clients_list_topic}")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def loop():
    threading.Timer(intervall_seconds, loop).start()
    publish_data()


mqclient = mqtt.Client()
mqclient.on_connect = on_connect
mqclient.on_message = on_message

mqclient.connect(broker_hostname, broker_port, 60)

# set last will message so that cached results will be overwritten
mqclient.will_set(clients_list_topic, payload=generate_payload({'clients': {}, 'isLastWill': True}),
                  retain=retain_messages)
if not retain_messages:
    # delete (may be existing) old retained messages
    mqclient.publish(clients_list_topic, retain=True)
    mqclient.publish(clients_count_topic, retain=True)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
loop()
mqclient.loop_forever()
