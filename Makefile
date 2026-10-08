.PHONY: install test lint run demo clean

install:
	pip install -e ".[dev]"

test:
	pytest --cov=normagraph --cov-report=term-missing

lint:
	ruff check normagraph tests

run:
	uvicorn normagraph.main:app --reload --port 8000

demo:
	python -m normagraph.cli demo

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
