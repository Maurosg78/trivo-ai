.PHONY: install test lint format clean docs docker-up docker-down

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

test:
	pytest

lint:
	flake8 .
	black . --check
	isort . --check-only
	mypy .

format:
	black .
	isort .

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name "site" -exec rm -r {} +
	find . -type d -name ".tox" -exec rm -r {} +
	find . -type d -name "build" -exec rm -r {} +
	find . -type d -name "dist" -exec rm -r {} +

docs:
	mkdocs serve

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build

docker-clean:
	docker-compose down -v
	docker system prune -f 