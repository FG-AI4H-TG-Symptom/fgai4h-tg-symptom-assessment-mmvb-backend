flake8:
	flake8 .

black-check:
	black --check --diff .

isort:
	isort -rc .

isort-check:
	isort -c -rc .

black:
	black .

lint: flake8 isort-check black-check

format: black isort
