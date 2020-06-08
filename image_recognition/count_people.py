
import boto3

IMAGE = "/Users/marvin/abgabenUniGit/aws-rekognition/supermarket.jpg"
BUCKET = "amazon-rek"
KEY = "supermarket"

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

# s3 = boto3.client('s3')
# with open(IMAGE, "rb") as f:
#     s3.upload_fileobj(f, BUCKET, KEY)

response_labels = detect_labels(BUCKET, KEY)
persons = [element for element in response_labels if element['Name'] == 'Person'][0]
print(len(persons['Instances']))