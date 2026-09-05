PYTHON ?= python3
MAIN := a_maze_ing.py
CONFIG ?= config.txt

.PHONY: install run debug clean lint lint-strict test syntax check

install:
	$(PYTHON) -m pip install -r requirements.txt

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
	$(PYTHON) -m compileall -q $(MAIN) mazegen

lint:
	$(PYTHON) -m flake8 $(MAIN) mazegen
	$(PYTHON) -m mypy $(MAIN) mazegen \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 $(MAIN) mazegen
	$(PYTHON) -m mypy $(MAIN) mazegen --strict

test:
	@$(PYTHON) -m pytest -v; status=$$?; \
	if [ $$status -eq 5 ]; then \
		echo "No tests found yet; skipping."; \
		exit 0; \
	fi; \
	exit $$status

check: syntax lint test
