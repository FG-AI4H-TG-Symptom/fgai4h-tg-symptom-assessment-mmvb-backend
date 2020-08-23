[back](../README.md)

## docker-compose setup
To run the whole backend including celery, mysql, redis, run:
```
docker-compose up --build
```

Backend and celery will still have auto reload, meaning that if you change a *.py file they should restart automatically.

### Structure of the docker setup
Our docker-compose.yml file has 4 services:
* backend
* celery
* mysql
* redis

All those services are able to communicate with each other.
Both the backend and celery use the same Dockerfile of the project be setup.

Backend uses a entrypoint script to run migrate, register_ais and load fixtures before starting the backend server.

#### Waiting for mysql and redis to be up and running
Especially mysql takes some time to start up. We need to wait for it to be available, so the backend and celery do not throw errors.

Therefore we use the wait script: [docker-compose-wait](https://github.com/ufoscout/docker-compose-wait)

We define the env var `WAIT_HOSTS: mysql:3306, redis:6379` and run the wait command before our actual command for backend and celery.
They will then wait until the services are available on defined port.

### Accessing host network from container
You may want to access your host from the docker containers, e.g. when registering a Toy AI not running inside the container.
To do this you need to use `host.docker.internal` as hostname.

Example URL for registering Toy AI running on localhost:8080: `http://host.docker.internal:8080`