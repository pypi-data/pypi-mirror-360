test: mypy _lint && check-format
    # Testing project
    @just _test

# Run test just on the current python version
test-single:
    # Test on current python version
    uv run pytest

check: mypy lint

# runs lints, but not type checking or tests
#
# Avoids performance penalty of `mypy`
lint: _lint && check-format

_lint:
    -uv run ruff check

fix: && _format fix-spelling
    @# Failure to fix should not prevent formatting
    -uv run ruff check --fix --unsafe-fixes

build: mypy && _test check-format
    # Build project
    uv build

mypy:
    uv run mypy src

# runs tests without anything else
_test:
    hatch test --all

# Check for spelling issues
spellcheck:
    # Check for obvious spelling issues
    uv run typos

# Fix obvious spelling issues
fix-spelling:
    # Fix obvious spelling issues
    uv run typos --write-changes

# Checks for formatting issues
check-format: && spellcheck
    uv run ruff format --check .
    uv run ruff check --select I --output-format concise .
    # Checking TOML file formatting
    RUST_LOG=WARN uv run taplo format --check

format: _format && spellcheck

_format:
    uv run ruff format .
    uv run ruff check --select 'I' --fix .
    RUST_LOG=WARN uv run taplo format
