.PHONY: install-pre-commit run-pre-commit generate-auto-migration migrate-head

install-pre-commit:
	poetry run pre-commit install

run-pre-commit:
	poetry run pre-commit run --all-files

generate-auto-migration:
	poetry run alembic revision --autogenerate

migrate-head:
	poetry run alembic upgrade head
