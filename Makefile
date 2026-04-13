run:
	uv run project/scripts/main.py
	
	
test:
	pytest tests/test_app.py -v
	
	
ruff:
	uv run ruff check .