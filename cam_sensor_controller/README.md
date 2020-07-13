# Camera Sensor Controller
This script takes images from the watch_folder and sends them to the Amazon Rekogniton service to count the number of people on the image.

Prerequisites
-------------
Set up your AWS authentication credentials. The credentials file is by default located at `~/.aws/credentials`.

```
pip install -r requirements.txt 
python camera_count.py
```