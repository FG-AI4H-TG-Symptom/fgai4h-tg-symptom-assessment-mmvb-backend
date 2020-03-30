# FGAI4H TG Symptom – MMVB backend

*This repository hosts the backend only. Find the frontend* 
*[in this repository](https://github.com/FG-AI4H-TG-Symptom/fgai4h-tg-symptom-benchmarking-frontend)* 
*and follow the instructions there.*

## Installation Instructions

The following instructions have been tested on a macOS, if you are using another development environment the instructions
might be a little bit different.

It will be assumed you have installed and use [Docker](https://www.docker.com/get-started), but you can install
uncontainerized local versions of the dependencies too.

### Virtual Environment

Create and activate a virtual environment with Python 3.7+.  
Python 3.8.1 is recommended; you can use pyenv to manage your Python installations.

```
$ python3 -m venv .venv
$ source .venv/bin/activate
```

### Install and Configure MySQL

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
docker run -p 3306:3306 --name fgai4h-tg-symptom-mmvb-mysql -e MYSQL_ROOT_PASSWORD='{your-password-here}' -d mysql 
```

Then connect to MySQL using the root user (supply the password you specified above):
```
docker exec -it fgai4h-tg-symptom-mmvb-mysql mysql -u root -p
```

You should now see a `mysql>` prompt and can continue with **Set up MySQL database** below.

#### Local install
As an initial step you might need to run the following for being able to start MySQL services in the next steps:
```
$ xcode-select --install
```

These steps assume you have [Homebrew](https://brew.sh/) installed.  
To install MySQL:
```
$ brew install mysql
$ brew install mysql-client
$ brew tap homebrew/services
$ brew services start mysql
```

Make sure to change `host` from `127.0.0.1` to `localhost` in `mmvb_backend/settings.py` in the `DATABASES` config.

Configure a new password for the root user:
```
$ mysqladmin -u root password '{your-password-here}'
```

Then connect to MySQL using the root user:
```
$ mysql -u root -p
```
and provide the password you configured when prompted.

You should now see a `mysql>` prompt and can continue with **Set up MySQL database** below.

#### Set up MySQL database

In the client console, create a system user with proper privileges and a new database to be used on the django project:
```
mysql> CREATE USER 'system'@'172.17.0.1' IDENTIFIED BY 'systemsecret';
mysql> GRANT ALL PRIVILEGES ON * . * TO 'system'@'172.17.0.1';
mysql> CREATE DATABASE mmvb;
mysql> quit
```
*Replace `127.0.0.1` with `localhost` if you are using a local MySQL installation (rather than via Docker)*


### Install project requirements

Install the Python MySQL client module with OpenSSL (the link path is specific to macOS/Homebrew):
```
LDFLAGS=-L/usr/local/opt/openssl/lib pip install mysqlclient
```

```
python -m pip install -r requirements.txt
```

### Include project in PYTHONPATH

```
export PYTHONPATH=$PYTHONPATH:./mmvb_backend
```

### Apply database schema

```
python manage.py migrate
```

### Create a superuser for admin website

This step will be useful for the future if/when we start using the admin interface from django. This will be the user with all admin privileges you will have to access that interface.
```
python manage.py createsuperuser
```
then provide an `username`, `email` and `password` (with confirmation).


## Run the application

```
python manage.py runserver
```

The application api will be running on [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)

To check the admin interface, go to [http://localhost:8000/admin/](http://localhost:8000/admin/)

There is an experimental auto-generated documentation on [http://localhost:8000/api/docs/](http://localhost:8000/admin/)
