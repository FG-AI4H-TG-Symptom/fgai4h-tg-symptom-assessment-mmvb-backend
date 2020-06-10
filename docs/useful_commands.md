[back](../README.md)

## Useful django and make commands
There are multiple useful individual commands for specific purposes and some commands that group them together to bring the application app. Those commands are briefly listed and explained in case you need to run them separetely, to really set up and run the whole application check

### Linting
This assumes you have activated your local virtual environment.
To run local linting and codestyle checks you can use
```
$ make lint
```
We use this in our CI process to make sure codestyle is being adhered to.

### MySQL database
You can shutdown the mysql database instance running on docker by running:
```
$ make stop_database
```

And you can start the database instance with:
```
$ make start_database
```

### Redis storage
You can shutdown the redis storage instance running on docker by running:
```
$ make stop_redis
```
**Make sure Celery is not still running tasks before doing it though**

You can start the database instance with:
```
$ make start_redis
```

### Database migrations
Whenever there are changes to your database models you need to run a django command to apply those changes to the database schema.
**Make sure mysql database is up and running before running this command.**
```
$ make apply_migrations
```

### Toy AIs registration
In a scenario where Toy AIs are being used, if you want to manually register them using the custom django command that was implemented for this purpose, just run:
```
$ make register_ais
```
**Make sure mysql database is up and running before running this command.**

### Celery
For running the celery workers you just need to run:
```
$ make start_celery
```
**Make sure mysql and redis are up and running before running this command.**
