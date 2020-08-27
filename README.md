# FGAI4H TG Symptom – MMVB backend

*This repository hosts the backend only. Find the frontend*
*[in this repository](https://github.com/FG-AI4H-TG-Symptom/fgai4h-tg-symptom-benchmarking-frontend)*
*and follow the instructions there.*

### Starting quickly using docker-compose
docker-compose allows to setup and start all services with one configuration file. More info on the setup: [docker-compose](./docs/docker-compose.md)

To run the whole backend including celery, mysql, redis, run:
```
docker-compose up --build
```

For instructions to run without docker-compose, see below.

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

Now, get the image and start up a container. Use the command from the [Makefile](./Makefile) for a quick setup.
It uses the provided `DB_ROOT_PWD` as root password.
```
make start_database
```

Then connect to MySQL using the root user (supply the password `DB_ROOT_PWD`, which is `rootsecret` by default):
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

To install test requirements, which includes tools for development (currently only pre-commit), run
```
$ make install_test_requirements
```

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


### Pre-commit hooks
This repository lints and tests code as a part of the CI process.
[Pre-commit](https://pre-commit.com/) is a project that you can use to run a suite of tools to check the codebase.

First [install pre-commit](https://pre-commit.com/#installation). Using homebrew on MacOS:
```
brew install pre-commit
```

To install the hooks that we use run:
```
make precommit_install
```

This will make sure the linting checks are run when trying to create a new commit, if any of the check fails the commit won't be created, so you will need to fix the issues, stage the changes, and try to commit again.

#### Celery
The project requires [Celery](https://docs.celeryproject.org/en/4.4.2/) (task queue) for some of its features (running benchmarks for example). For being able
to use Celery we need a message broker, we decided to use [Redis](https://redis.io/).

### Django admin interface
This is currently not being used for the application but might be useful in the future as the django admin interface is a simple yet very powerful and extensible tool.

#### Create superuser for Django Admin

This step will be useful for the future if/when we start using the admin interface from django. This will be the user with all admin privileges to have to access that interface.
**Make sure you have activated your virtual environment.**
```
$ python manage.py createsuperuser
```
then provide an `username`, `email` and `password` (with confirmation).

## Useful django and make commands
Check the [useful commands](./docs/useful_commands.md) section for a list and brief explanation of the available django and make commands.

## General Tips
For some general tips on development-related topics, such as database migrations and celery tasks implementation, check the [general tips](./docs/general_tips.md) section.

## Django and Django Rest Framework
Check the [Django and DRF](./docs/django_and_drf.md) section for more information on the project structure and the mentioned frameworks.

## Project applications
You can find a brief explanation about the scope of each django application developed for the `mmvb_backend` project [here](./docs/mmvb_apps.md).
