start:
	npx concurrently 'npx start-hexlet-devops-deploy-crud-frontend' 'make run'

run:
	uv run application/main.py

tests:
	uv run pytest application/test_links_repository.py -vv
	uv run pytest application/test_app.py -vv

ruff:
	uv run ruff check .
	uv run ruff format --check .