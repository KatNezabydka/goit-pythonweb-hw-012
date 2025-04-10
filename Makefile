MIGRATION_COMMAND = poetry run alembic upgrade head
MIGRATION_UPDATE_COMMAND = poetry run alembic revision --autogenerate

.PHONY: setup \
        migrate \
		lint \
		help

venv/bin/activate: ## Alias for virtual environment
	python3 -m venv venv

setup: venv/bin/activate ## Project setup
	. venv/bin/activate; pip install --upgrade pip
	. venv/bin/activate; pip install poetry
	. venv/bin/activate; poetry install

migrate:
	docker compose exec app $(MIGRATION_COMMAND)

migration-update:
	docker compose exec app $(MIGRATION_UPDATE_COMMAND)

lint: ## Run linter
	. venv/bin/activate; ruff format --config ./pyproject.toml . && ruff check --fix --config ./pyproject.toml .

# Just help
help: ## Display help screen
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

test: ## Run tests check
	poetry run pytest $(filter-out $@,$(MAKECMDGOALS)) -s