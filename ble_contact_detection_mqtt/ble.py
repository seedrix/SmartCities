from bluepy.btle import Scanner, DefaultDelegate, ScanEntry, UUID
import paho.mqtt.client as mqtt
import hashlib
import json
import subprocess

interface_number = 0
command_mac = 'hciconfig hci' + str(interface_number) + ' | grep -oE "([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}"'


def get_mac():
    process = subprocess.run(command_mac, stdout=subprocess.PIPE, shell=True)
    result = process.stdout.decode('utf-8')
    return 'b' + result.strip()


broker_hostname = "broker.hivemq.com"
broker_port = 1883

retain_messages = False

interval_seconds = 30.0

namespace = 'de/smartcity/2020/mymall'
clients_list_topic = namespace + '/sensors/ble/' + get_mac() + '/list'
clients_count_topic = namespace + '/sensors/ble/' + get_mac() + '/count'

contact_detection_service_uuid = str(UUID("fd6f"))
print("contact_detection_service_uuid: ", contact_detection_service_uuid)


def publish_data(mqclient, results):
    print(f"Connected clients ({results.get_device_count()}): {results.get_device_list()}")
    mqclient.publish(clients_count_topic, payload=generate_payload({'count': results.get_device_count()}),
                     retain=retain_messages)
    mqclient.publish(clients_list_topic, payload=generate_payload({'clients': results.get_device_list_hashed()}),
                     retain=retain_messages)
    print("published data")


def generate_payload(data):
    payload = {'sensor_id': get_mac(), 'sensor_type': 'ble'}
    payload.update(data)
    print(payload)
    return json.dumps(payload)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print(f"Using the following topics to publish data:\n\t{clients_count_topic}\n\t{clients_list_topic}")
    # set last will message so that cached results will be overwritten
    client.will_set(clients_list_topic, payload=generate_payload({'clients': [], 'isLastWill': True}),
                    retain=retain_messages)

    if not retain_messages:
        # delete (may be existing) old retained messages
        client.publish(clients_list_topic, retain=True)
        client.publish(clients_count_topic, retain=True)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def device_is_relevant(dev):
    return dev.getValueText(ScanEntry.COMPLETE_16B_SERVICES) == contact_detection_service_uuid


class Results:
    def __init__(self):
        self.devices = {}

    def add_device(self, dev_id):
        self.devices[dev_id] = True

    def get_device_list(self):
        return list(self.devices.keys())

    def get_device_count(self):
        return len(self.devices)

    def get_device_list_hashed(self):
        return list(map(lambda x: self.hash_entry(x), self.get_device_list()))

    @staticmethod
    def hash_entry(entry):
        # Todo: hashing
        return hashlib.sha224(entry.encode()).hexdigest()

    def clear(self):
        self.devices = {}


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev and device_is_relevant(dev):
            print("Discovered relevant device ", dev.addr)


print("Station: ", get_mac())
mqclient = mqtt.Client()
mqclient.on_connect = on_connect
mqclient.on_message = on_message
mqclient.connect(broker_hostname, broker_port, 60)

results = Results()
scanner = Scanner(iface=interface_number).withDelegate(ScanDelegate())
scanner.start(passive=True)

mqclient.loop_start()
while True:
    scanner.process(timeout=interval_seconds)
    devices = scanner.getDevices()
    results.clear()
    scanner.clear()

    for dev in devices:
        print(f"Device {dev.addr} ({dev.addrType}), RSSI=%{dev.rssi} dB")
        print("\t ", str(dev.getValue(ScanEntry.COMPLETE_16B_SERVICES)))
        if device_is_relevant(dev):
            data = dev.getValue(ScanEntry.SERVICE_DATA_16B)
            rolling_proximity_id = ''.join('{:02x}'.format(x) for x in data[2:])
            # first 2 bytes are the 16 bit service identifier, so the should be 0xfd6f
            if data[1] != 0xfd and data[0] != 0x6f:
                # should never happen. invariant violated.
                print("Service identifier of payload does not match (expected 0xfd 0x6f): ", hex(data[1]), hex(data[0]))
                for (adtype, desc, value) in dev.getScanData():
                    print(f" {adtype}: {desc} = {value}")
            results.add_device(rolling_proximity_id)
            print("Found ID: ", rolling_proximity_id)
        # for (adtype, desc, value) in dev.getScanData():
        #    print(f" {adtype}: {desc} = {value}")
    print(f"Found {results.get_device_count()}  devices")
    # Todo: Mqtt stuff
    publish_data(mqclient, results)
