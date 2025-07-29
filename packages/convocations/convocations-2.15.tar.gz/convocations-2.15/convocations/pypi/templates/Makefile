SHELL := /bin/bash
VERSION := $(shell lsb_release -rs)
BUMP=minor
export BUMP
.PHONY: help

help:  ## help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup:  ## creates local virtual environment and installs requirements
	@if which python3.13 && [ ! -d bin ] ; then python3.13 -m venv . ; fi
	@if which python3.12 && [ ! -d bin ] ; then python3.12 -m venv . ; fi
	@if which python3.11 && [ ! -d bin ] ; then python3.11 -m venv . ; fi
	@if which python3.10 && [ ! -d bin ] ; then python3.10 -m venv . ; fi
	@source bin/activate \
	  && python -m pip install -U wheel \
	  && pip install -r requirements.txt

test: FORCE  ## runs unit / integration tests via pytest
	source bin/activate \
	  && pytest -v -x test --cov {{ name }} --cov-report term-missing

build:  ## builds an sdist bundle
	source bin/activate \
	  && python -B -O setup.py sdist

lint:  ## performs linting via flake8 and pylint
	source bin/activate && flake8 {{ name }}
	source bin/activate && pylint --rcfile .pylintrc {{ name }}

clean:  ## cleans egg-info and dist directory
	source bin/activate \
	  && python -B -O setup.py clean
	rm -rf dist build
	rm -rf {{ name }}.egg-info

version:  ## bumpversion minor
	source bin/activate \
	  && bumpversion $(BUMP)
	git push --follow-tags

upload:  ## uploads built sdist bundles to pypi using twine
	source bin/activate \
	  && twine upload dist/*

publish: clean version build upload  ## performs a clean, version, build, and upload

FORCE:
