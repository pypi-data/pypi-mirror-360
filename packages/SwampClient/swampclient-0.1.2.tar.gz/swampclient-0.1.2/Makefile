.PHONY: init install test build upload clean

init: clean
	pip install -r requirements.txt

create:
	python3 -m venv .venv

install:
	pip install -e .

test:
	PYTHONPATH=src python -m unittest discover

build: init
	python3 -m build

upload: build
	python3 -m twine upload dist/*

clean:
	rm -rf dist
	find . -type d -name '__pycache__' -exec rm -rf {} +
