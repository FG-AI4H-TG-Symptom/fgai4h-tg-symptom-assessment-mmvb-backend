### Brief Installation Instructions ###

The following instructions have been tested on a mac, if you are using another development environment the instructions
might be a little bit different.

#### Virtual Environment ####

Create and activate a virtual environment with Python 3.8.1. You can use pyenv to manage your Python installations.
```
$ python -m venv .venv
$ source .venv/bin/activate
```

And make sure to update your python path for the next steps
```
export PYTHONPATH=$PYTHONPATH:./mmvb_backend
```

#### Install and Configure MySQL ####
As an initial step you might need to run the following for being able to start MySQL services in the next steps:
```
$ xcode-select --install
```

These steps assume you have homebrew installed

First, install it:
```
$ brew install mysql
$ brew install mysql-client
$ brew tap homebrew/services
$ brew services start mysql
```

Configure a new password for the root user:
```
$ mysqladmin -u root password '{your-password-here}'
```

Then connect to MySQL using the root user:
```
$ mysql -u root -p
```
and provide the password you configured when prompted.

In the client console, create a system user with proper privileges and a new database to be used on the django project:
```
mysql> CREATE USER 'system'@'localhost' IDENTIFIED BY 'systemsecret';
mysql> GRANT ALL PRIVILEGES ON * . * TO 'system'@'localhost';
mysql> CREATE DATABASE mmvb;
mysql> quit
```

Finally, install the Python MySQL client module with openssl:
```
LDFLAGS=-L/usr/local/opt/openssl/lib pip install mysqlclient
```

#### Install project requirements ####

```
python -m pip install -r requirements.txt
```

#### Celery setup
For using Celery (task queue) we will need to setup a message broker. Redis should be a good option.
You should be able to download the proper docker image and run it with the following commands:

```
$ docker pull redis
$ docker run -p 6379:6379 --name fgai4h-tg-symptom-mmvb-redis -d redis
```

On a dedicated shell, run the Celery worker server:

```
celery -A mmvb_backend worker -l info
```

#### Apply database schema ####

```
python manage.py migrate
```

#### Create a superuser for admin website ####

This step will be useful for the future if/when we start using the admin interface from django. This will be the user with all admin privileges you will have to access that interface.
```
python manage.py createsuperuser
```
then provide an `username`, `email` and `password` (with confirmation).


#### Run the application ####

```
python manage.py runserver
```

The application api will be running on http://localhost:8000/api/v1/

To check the admin interface, go to http://localhost:8000/admin/

There is an experimental auto-generated documentation on http://localhost:8000/api/docs/


#### General Tips ####

It is always useful to run `python manage.py migrate` after you checked out code from someone, as the data models/schema might
have changed and you need to persist them.

If/when you implement a new data model, you need to run:
```
$ python manage.py makemigrations
$ python manage.py migrate
```

to generate the schema changes and apply them to the database.


If you need to implement new celery tasks for any of your Django installed apps (the ones listed under `INSTALLED_APPS` in the project `settings.py` module) you only need to:

  - Create (if not already created) a `tasks.py` module under the desired Django app directory (`cases` for example)
  - Follow the template shown below on your `tasks.py`:
  ```
  from celery import shared_tasks

  @shared_tasks
  def add(x, y):
      return x + y
  ```

Then you could simply import the `add` task somewhere in your code and run it and, if the celery worker server is up and running, your task would be executed.

For more details check the [celery docs](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html).