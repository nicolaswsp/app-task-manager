PYTHON ?= python
UV ?= uv
HOST ?= 127.0.0.1
PORT ?= 8000

.PHONY: install run test

install:
	$(UV) sync

run:
	$(UV) run uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

test:
	$(UV) run pytest
