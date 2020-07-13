# Data service: mqtt_2_mongo

Stores all MQTT messages of specified topics to a MONGO DB.
This code is based on https://github.com/David-Lor/MQTT2MongoDB/.


## Run
Set the list of relevant topics (`mqtt.py`) and configure the database (`mongo_handler.py`)
Then execute from the root directory

```
pip install -r mqtt_2_mongo/requirements.txt 
python -m mqtt_2_mongo
```