PYTHON := python3
MAIN := a_maze_ing.py
CONFIG ?= config.txt

.PHONY: install run debug clean lint lint-strict test syntax check

install:
	$(PYTHON) -m pip install flake8 mypy pytest

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

syntax:
	$(PYTHON) -m compileall -q .

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

test:
	$(PYTHON) -m pytest -v

check: syntax lint test
