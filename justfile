# List all recipes.
default:
    @just --list

# Run all tests.
test:
    uv run pytest --disable-warnings --log-level=1 --cov=src/analytix --cov-report=term-missing

# Format code (currently only checks).
format:
    uvx black src/analytix/ tests/

# Lint code.
lint:
    uvx ruff check src/analytix/ --fix

# Check typing.
typecheck:
    uv run mypy src/analytix/

# Check slots are set up correctly.
check-slots:
    uvx --with . slotscheck -m analytix

# Check spelling.
check-spelling:
    uvx codespell src/analytix/ tests/ -S "src/analytix/reports/data.py"

# Serve the documentation.
serve-docs:
    uv run mkdocs serve --watch src/analytix/

# Run all checks.
run-checks: test format lint typecheck check-slots check-spelling
