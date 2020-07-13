import boto3
import hashlib
import paho.mqtt.client as mqtt
import time
import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


broker_hostname = "broker.hivemq.com"
broker_port = 1883

path_to_watch = "./watch_folder/"

interface = "camera0"
namespace = 'de/smartcity/2020/mymall'
camera_count_topic = namespace + '/sensors/cam/c'+interface+'/count'

BUCKET = "amazon-rek"

def detect_labels(bucket, key, max_labels=10, min_confidence=90, region="us-east-1"):
	rekognition = boto3.client("rekognition", region)
	response = rekognition.detect_labels(
		Image={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		MaxLabels=max_labels,
		MinConfidence=min_confidence,
	)
	return response['Labels']

def generate_key(filename):
	sha256_hash = hashlib.sha256()
	with open(filename,"rb") as f:
		# Read and update hash string value in blocks of 4K
		for byte_block in iter(lambda: f.read(4096),b""):
			sha256_hash.update(byte_block)
		file_extension = os.path.splitext(filename)[1]
	return sha256_hash.hexdigest() + file_extension


def upload_image(image, bucket, key):
	s3 = boto3.client('s3')
	with open(image, "rb") as f:
		s3.upload_fileobj(f, bucket, key)

def get_number_of_persons(response):
	persons = [element for element in response if element['Name'] == 'Person'][0]
	return len(persons['Instances'])

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print(f"Connected with result code {rc}")
	print(f"Using the following topics to publish data:\n\t{camera_count_topic}")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def publish_data(num_of ):
    print(f"Connected clients ({len(clients)}): {clients}")


def generate_payload(data):
    payload = {'sensor_id': 'c'+interface, 'sensor_type': 'cam'}
    payload.update(data)
    print(payload)
    return json.dumps(payload)

def watchdog_on_created(event):
	print(f"{event.src_path} has been created")
	image = event.src_path
	key = generate_key(image)
	upload_image(image, BUCKET, key)
	response_labels = detect_labels(BUCKET, key)
	person_count = get_number_of_persons(response_labels)
	mqclient.publish(camera_count_topic, payload=generate_payload({'count': person_count}))
	print("published data")


mqclient = mqtt.Client()
mqclient.on_connect = on_connect
mqclient.on_message = on_message
mqclient.connect(broker_hostname, broker_port, 60)

patterns = "*"
ignore_patterns = ""
ignore_directories = False
case_sensitive = True
my_event_handler = FileSystemEventHandler()
my_event_handler.on_created = watchdog_on_created

if not os.path.exists(path_to_watch):
    os.makedirs(path_to_watch)


my_observer = Observer()
my_observer.schedule(my_event_handler, path=path_to_watch, recursive=True)
my_observer.start()

mqclient.loop_forever()