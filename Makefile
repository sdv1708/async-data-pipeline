.PHONY: dev-bootstrap compose-up compose-down lint test fmt

dev-bootstrap:
	pip install -U pip pre-commit
	pre-commit install

compose-up:
	docker compose up -d

compose-down:
	docker compose down

lint:
	pre-commit run --all-files

test:
	pytest -q

fmt:
	black . && isort .
