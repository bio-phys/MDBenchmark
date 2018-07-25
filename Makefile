.PHONY: build clean clean-build clean-pyc clean-test upload reformat reformat-check flake8 rst-lint

clean: clean-build clean-pyc clean-test

clean-build:
	rm -rf build/
	rm -rf dist/

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test:
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/

build: clean
	python setup.py sdist bdist_wheel --universal

upload: build
	twine upload dist/*

reformat:
	black setup.py mdbenchmark/

reformat-check:
	black --check setup.py mdbenchmark/

flake8:
	flake8 mdbenchmark/

rst-lint:
	rst-lint README.rst
