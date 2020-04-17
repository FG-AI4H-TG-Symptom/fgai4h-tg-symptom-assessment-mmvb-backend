PYTHONPATH := ./mmvb_backend : $(PYTHONPATH)

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
