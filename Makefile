# Local checks. No CI in this repo: run `make check` before every push.
SHELL := /bin/bash

.PHONY: check lint test

check: lint test

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest -q
