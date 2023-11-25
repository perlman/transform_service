# Fly Coordinate Query & Conversion Service

This code is based on [CloudVolumeServer](https://github.com/flyconnectome/CloudVolumeServer).

## Run the web service locally
```uvicorn --reload app.main:app```

## Run tests
```pytest```


## For deploymen

Use gunicorn+guvicorn worker for deployment:
```
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```
