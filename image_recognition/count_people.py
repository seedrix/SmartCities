import boto3
import hashlib

IMAGE = "images/image_1.png"
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
	return sha256_hash.hexdigest()


def upload_image(image, bucket, key):
	s3 = boto3.client('s3')
	with open(image, "rb") as f:
		s3.upload_fileobj(f, bucket, key)

def get_number_of_persons(response):
	persons = [element for element in response_labels if element['Name'] == 'Person'][0]
	return len(persons['Instances'])


key = generate_key(IMAGE)
print(f'Key : {key}')
upload_image(IMAGE, BUCKET, key)
response_labels = detect_labels(BUCKET, key)
print(get_number_of_persons(response_labels))

