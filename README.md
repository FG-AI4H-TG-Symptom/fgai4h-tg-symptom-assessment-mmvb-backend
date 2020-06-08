# FGAI4H TG Symptom – MMVB backend

*This repository hosts the backend only. Find the frontend*
*[in this repository](https://github.com/FG-AI4H-TG-Symptom/fgai4h-tg-symptom-benchmarking-frontend)*
*and follow the instructions there.*

## Installation Instructions

The following instructions have been tested on a macOS, if you are using another development environment the instructions
might be a little bit different.

It will be assumed you have installed and use [Docker](https://www.docker.com/get-started).

### Virtual Environment

Create and activate a virtual environment with Python 3.7+.
Python 3.8.1 is recommended; you can use [pyenv](https://github.com/pyenv/pyenv) to manage your Python installations.
```
$ python3 -m venv .venv
$ source .venv/bin/activate
```

You might need to update your python path for the next steps
```
export PYTHONPATH=$PYTHONPATH:./mmvb_backend
```

### Pre-commit hooks

This repository lints and tests code as a part of the CI process.
[Pre-commit][pre-commit] is a project that you can use to run a suite of tools to check the codebase.

To install the hooks that we use run:
```
make precommit_install
```

This will make sure the linting checks are run when trying to create a new commit, if any of the check fails the commit won't be created, so you will need to fix the issues, stage the changes, and try to commit again.

### Install and Configure MySQL with Docker

#### Docker

Although MySQL will be running in a container you need a local MySQL connector. On macOS you can install it with
```
brew install mysql-connector-c
```
and add it to your PATH (source `~/.zshrc` or re-open your terminal after this step)
```
echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.zshrc
```

Now, get the image and start up a container
```
docker pull mysql
docker run -p 3306:3306 --name fgai4h-tg-symptom-mmvb-mysql -e MYSQL_ROOT_PASSWORD='{your-root-password-here}' -d mysql
```

Then connect to MySQL using the root user (supply the password you specified above):
```
docker exec -it fgai4h-tg-symptom-mmvb-mysql mysql -u root -p
```

You should now see a `mysql>` prompt and can continue with **Set up MySQL database** below.

#### Set up MySQL database

In the client console, create a system user with proper privileges and a new database to be used on the django project:
```
mysql> CREATE USER 'system'@'172.17.0.1' IDENTIFIED BY 'systemsecret';
mysql> GRANT ALL PRIVILEGES ON * . * TO 'system'@'172.17.0.1';
mysql> CREATE DATABASE mmvb;
mysql> quit
```

### Install project requirements
You might need to install openssl:

```
$ brew install openssl
```

This section assumes the use of the pyenv.

Install the Python MySQL client module with OpenSSL (the link path is specific to macOS/Homebrew):
```
$ LDFLAGS=-L/usr/local/opt/openssl/lib pip install mysqlclient
```

The requirements for running the server locally can be installed by
```
$ make install_requirements
```

To install test requirements, which includes tools for development, run
```
$ make install_test_requirements
```

#### Celery
The project requires [Celery](https://docs.celeryproject.org/en/4.4.2/) (task queue) for some of its features (running benchmarks for example). For being able
to use Celery we need a message broker, we decided to use [Redis](https://redis.io/).

The following session brings together useful commands for running the application, which includes the commands for setting up
Redis and Celery.

### Useful django and make commands:
There are multiple useful individual commands for specific purposes and some commands that group them together to bring the application app. Those commands are briefly listed and explained in case you need to run them separetely, to really set up and run the whole application check

#### Linting
This assumes you have activated your local virtual environment.
To run local linting and codestyle checks you can use
```
$ make lint
```
We use this in our CI process to make sure codestyle is being adhered to.

#### MySQL database
You can shutdown the mysql database instance running on docker by running:
```
$ make stop_database
```

And you can start the database instance with:
```
$ make start_database
```

#### Redis storage
You can shutdown the redis storage instance running on docker by running:
```
$ make stop_redis
```
**Make sure Celery is not still running tasks before doing it though**

You can start the database instance with:
```
$ make start_redis
```

#### Database migrations
Whenever there are changes to your database models you need to run a django command to apply those changes to the database schema.
**Make sure mysql database is up and running before running this command.**
```
$ make apply_migrations
```

#### Toy AIs registration
In a scenario where Toy AIs are being used, if you want to manually register them using the custom django command that was implemented for this purpose, just run:
```
$ make register_ais
```
**Make sure mysql database is up and running before running this command.**

#### Celery
For running the celery workers you just need to run:
```
$ make start_celery
```
**Make sure mysql and redis are up and running before running this command.**

### Django admin interface
This is currently not being used for the application but might be useful in the future as the django admin interface is a simple yet very powerful and extensible tool.

#### Create superuser for Django Admin

This step will be useful for the future if/when we start using the admin interface from django. This will be the user with all admin privileges to have to access that interface.
**Make sure you have activated your virtual environment.**
```
$ python manage.py createsuperuser
```
then provide an `username`, `email` and `password` (with confirmation).

## Running the application

For running the application you need to have configured the mysql database as explained in the previous sessions.
You will need 2 different shells for this, one for running the command the brings up mysql, redis and the application itself:
```
$ make start_app
```
In this shell you will have the running application with auto reload, meaning that if you change a *.py file the application should restart automatically.

And another one to run the celery workers:
```
$ make start_celery
```
In this shell you will have the celery workers with auto reload, meaning that if you change a *.py file the workers should restart automatically.

The application api will be running on [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)

To check the admin interface, go to [http://localhost:8000/admin/](http://localhost:8000/admin/)

There is an experimental auto-generated documentation on [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

For stopping the whole structure, go to the shell that is running the application and press `ctrl+C`, this should stop the django application, you just need to further run `make stop_app` in order to stop redis, mysql and celery.

## General Tips

### Migrations

It is always useful to run `make apply_migrations` after you checked out code from someone, as the data models/schema might
have changed and you need to persist them. **Make sure mysql is running before trying to apply migrations**

If/when you implement a new data model, you need to run:
```
$ python manage.py makemigrations
$ python manage.py migrate
```

to generate the schema changes and apply them to the database.

### Celery

If you need to implement new celery tasks for any of your Django installed apps (the ones listed under `INSTALLED_APPS` in the project `settings.py` module) you only need to:

  - Create (if not already created) a `tasks.py` module under the desired Django app directory (`cases` for example)
  - Follow the template shown below on your `tasks.py`:
  ```
  from celery import shared_task

  @shared_task
  def add(x, y):
      return x + y
  ```

Then you could simply import the `add` task somewhere in your code and run it and, if the celery worker server is up and running, your task would be executed.

For more details check the [celery docs](https://docs.celeryproject.org/en/4.4.2/django/first-steps-with-django.html).
