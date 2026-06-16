.PHONY: run test lint install

VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

install:
	$(PIP) install -r requirements.txt

run:
	$(VENV)/bin/streamlit run app.py

test:
	$(PYTHON) -m pytest tests/ -v

lint:
	$(VENV)/bin/flake8 app.py pipelines/ tests/ --max-line-length=100
