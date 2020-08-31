#!/bin/sh
/wait
python manage.py migrate
python manage.py register_ais
python manage.py loaddata case_sets.json cases.json benchmarking_sessions.json

exec "$@"