To run the frontend_service from the root directory, place your secret key in `.env` and execute the following commands:

```
pip install -r frontend_service/requirements.txt 
export FRONTEND_SERVICE_ENV_FILE_LOCATION=./.env
python -m frontend_service
```