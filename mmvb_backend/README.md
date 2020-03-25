### Brief Instalation Instructions ###

The following instructions have been tested on a mac, if you are using another development environment the instructions
might be a little bit different.

#### Virtual Environment ####

Create and activate a virtual environment with Python 3.8.1. You can use pyenv to manage your Python installations.

```
$ python -m venv .venv
$ source .venv/bin/activate
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