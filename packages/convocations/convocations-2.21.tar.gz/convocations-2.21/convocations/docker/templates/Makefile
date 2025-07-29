SHELL := /bin/bash
build:
	source venv/bin/activate \
	  && convoke build
setup:
	@if which python3.13 && [ ! -d venv/bin ] ; then python3.13 -m venv venv ; fi
	@if which python3.12 && [ ! -d venv/bin ] ; then python3.12 -m venv venv ; fi
	@if which python3.11 && [ ! -d venv/bin ] ; then python3.11 -m venv venv ; fi
	@if which python3.10 && [ ! -d venv/bin ] ; then python3.10 -m venv venv ; fi
	@if [[ ! -e ./venv/bin/python ]] ; then python3.9 -m venv venv ; fi
	source venv/bin/activate \
	  && pip install -U wheel \
	  && pip install -r requirements.txt
publish:
	source venv/bin/activate \
	  && convoke publish
