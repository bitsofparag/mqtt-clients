.PHONY: build clean clean-test clean-pyc clean-build lint docs help
.DEFAULT_GOAL := help
SHELL=/bin/bash
ENVIRONMENT := dev


define BROWSER_PYSCRIPT
import os, webbrowser, sys
from urllib.request import pathname2url
webbrowser.get('firefox').open_new_tab("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT


define PRINT_HELP_PYSCRIPT
import re, sys
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

SRC=mqtt_clients  # Update with correct path of src files
BROWSER := python -c "$$BROWSER_PYSCRIPT"
PYTHON_VERSION ?= 3.9.5
PROJECT_ROOT := $(PWD)
DEPLOY_ROOT := $(PWD)/deploy

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr .eggs/
	find . -name 'dist' -exec rm -rf {} + 2>/dev/null
	find . -name 'build' -exec rm -rf {} + 2>/dev/null
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts and logs
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '*.log*' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

test: ## run tests
	ENVIRONMENT=test nose2 -v --pretty-assert

lint: ## check style with flake8
	flake8 $(SRC) tests
	isort $(SRC) --ac -c

format: ## format py files
	isort $(SRC)

docs: ## generate Sphinx HTML documentation
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/build/html/index.html
