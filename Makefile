export PYTHONPATH := $(pwd):./mmvb_backend:$(PYTHONPATH)
export DB_ROOT_USER := root
export DB_ROOT_PWD := rootsecret
export DB_NAME := mmvb
export DB_PORT := 3306
export DB_USER := system
export DB_PWD := systemsecret
export DB_CONTAINER := fgai4h-tg-symptom-mmvb-mysql
export REDIS_CONTAINER := fgai4h-tg-symptom-mmvb-redis
export REDIS_PORT := 6309


precommit:
	pre-commit run -a

lint: precommit

.venv/:
	python3 -m venv .venv

precommit_install: .venv/
	. .venv/bin/activate; \
	pre-commit install

install_requirements: .venv/
	. .venv/bin/activate; \
	pip install -r requirements.txt

install_test_requirements: .venv/
	. .venv/bin/activate; \
	pip install -r test_requirements.txt

apply_migrations:
	. .venv/bin/activate; \
	python manage.py migrate

register_ais:
	. .venv/bin/activate; \
	python manage.py register_ais

stop_database:
	docker stop $(DB_CONTAINER) || true && docker rm -f $(DB_CONTAINER) || true

start_database: stop_database
	docker pull mysql; \
	docker run -p $(DB_PORT):$(DB_PORT) --name $(DB_CONTAINER) -v mysql:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=$(DB_ROOT_PWD) -d mysql

stop_redis:
	docker stop $(REDIS_CONTAINER) || true && docker rm -f $(REDIS_CONTAINER) || true; \

start_redis: stop_redis
	docker pull redis; \
	docker run -p $(REDIS_PORT):$(REDIS_PORT) --name $(REDIS_CONTAINER) -d redis redis-server --appendonly yes

start_celery:
	watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery worker -A mmvb_backend -l info

start_app:
	$(MAKE) start_database && \
	$(MAKE) start_redis && \
	$(MAKE) apply_migrations && \
	$(MAKE) register_ais && \
	. .venv/bin/activate; \
	python manage.py runserver

stop_app: stop_database stop_redis
	kill `ps aux | grep [c]elery | awk '{print $$2}'`
