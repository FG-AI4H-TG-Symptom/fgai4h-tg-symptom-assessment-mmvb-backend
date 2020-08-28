[back](../README.md)

## docker-compose setup
To run the whole backend including celery, mysql, redis, run:
```
docker-compose up --build
```

Backend and celery will still have auto reload, meaning that if you change a *.py file they should restart automatically.

#### Also run the webapp
Webapp located at [GitHub](https://github.com/FG-AI4H-TG-Symptom/fgai4h-tg-symptom-benchmarking-frontend)
can also be run using docker-compose.
This can be used as an easy way to run the whole system.
For a true production system something like Kubernetes should be used.

First copy the [`.env.example`](../.env.example) to `.env` and adjust it to
point to where the backend api is hosted.
This is needed because the webapp Docker image hardcodes the URL when building.

```
REACT_APP_BACKEND_BASE_URL=https://your-backend-server.com/api/v1
```

For building or when code changes:
```
docker-compose -f docker-compose.yml -f docker-compose.webapp.yml build
```

Afterwards to start use:
```
docker-compose -f docker-compose.yml -f docker-compose.webapp.yml up
```


### Structure of the docker setup
Our `docker-compose.yml` file has 4 services:
* backend
* celery
* mysql
* redis

All those services are able to communicate with each other.
Both the backend and celery use the same Dockerfile of the project be setup.

Backend uses a entrypoint script to run migrate, register_ais and load fixtures before starting the backend server.

Our `docker-compose.web.yml` file has only the webapp as service.
Specifying both .yml files combines them to one configuration.
Currently we fetch the GitHub repository of the webapp to build the image,
since we need to patch in the backend URL.

#### Waiting for mysql and redis to be up and running
Especially mysql takes some time to start up. We need to wait for it to be available, so the backend and celery do not throw errors.

Therefore we use the wait script: [docker-compose-wait](https://github.com/ufoscout/docker-compose-wait)

We define the env var `WAIT_HOSTS: mysql:3306, redis:6379` and run the wait command before our actual command for backend and celery.
They will then wait until the services are available on defined port.

### Accessing host network from container
You may want to access your host from the docker containers, e.g. when registering a Toy AI not running inside the container.
To do this you need to use `host.docker.internal` as hostname.

Example URL for registering Toy AI running on localhost:8080: `http://host.docker.internal:8080`