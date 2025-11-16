.PHONY: fixtures fixtures-force test

# Generate/refresh test PDF fixtures (requires ReportLab as a dev dependency)
fixtures:
	poetry run python tests/tools/generate_fixtures.py --out tests/data/library

# Force-regenerate all fixtures, overwriting existing files
fixtures-force:
	poetry run python tests/tools/generate_fixtures.py --out tests/data/library --force

# Run test suite via Poetry
test:
	poetry run pytest -q

