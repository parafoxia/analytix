# List all recipes.
default:
    @just --list

# Run all tests.
test:
    uv run pytest --disable-warnings --log-level=1 --cov=analytix --cov-report=term-missing

# Format code (currently only checks).
format:
    uvx black analytix/ tests/ examples/

# Lint code.
lint:
    uvx ruff check analytix/ --fix

# Check typing.
typecheck:
    uvx --with ".[dev]" --with pip mypy --install-types --non-interactive analytix/ examples/

# Check slots are set up correctly.
check-slots:
    uvx --with . slotscheck -m analytix

# Check spelling.
check-spelling:
    uvx codespell analytix/ tests/ examples/ -S "analytix/reports/data.py"

# Serve the documentation.
serve-docs:
    uv run mkdocs serve --watch analytix/
