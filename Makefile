PYTHON ?= python

.PHONY: install fetch build site test lint all serve clean

install:
	$(PYTHON) -m pip install -e ".[dev]"

fetch:
	$(PYTHON) -m mainstreet_atlas.cli fetch

build:
	$(PYTHON) -m mainstreet_atlas.cli build

site:
	$(PYTHON) -m mainstreet_atlas.cli generate-site

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

all:
	$(PYTHON) -m mainstreet_atlas.cli all

serve:
	$(PYTHON) -m http.server 8000 -d site/dist

clean:
	$(PYTHON) -m mainstreet_atlas.cli clean
