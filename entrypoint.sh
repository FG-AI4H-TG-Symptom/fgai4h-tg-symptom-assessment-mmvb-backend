#!/bin/sh
/wait
python manage.py migrate
python manage.py register_ais

exec "$@"