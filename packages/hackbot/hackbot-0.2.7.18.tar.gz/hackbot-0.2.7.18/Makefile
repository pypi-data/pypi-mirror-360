# ANSI color codes
GREEN=\033[0;32m
YELLOW=\033[0;33m
RED=\033[0;31m
BLUE=\033[0;34m
RESET=\033[0m

PROJECT_ROOT=.
PYTHON=PYTHONPATH=$(PROJECT_ROOT):$(PYTHONPATH) rye run python
PYTEST=PYTHONPATH=$(PROJECT_ROOT):$(PYTHONPATH) rye run pytest

########################################################
# Check dependencies
########################################################
.PHONY: check_rye
check_rye: ## Ensure rye is installed
	@echo "$(YELLOW)🔍Checking rye version...$(RESET)"
	@if ! command -v rye > /dev/null 2>&1; then \
		echo "$(RED)🚩rye is not installed. Please install rye before proceeding.$(RESET)"; \
		exit 1; \
	else \
		rye --version; \
	fi

install_dev_deps: check_rye
	rye sync

########################################################
# Tests
########################################################
.PHONY: test-live test-local test ensure_test_env
test: install_dev_deps
	$(PYTEST) tests/test_package.py tests/test_commands.py tests/test_utils.py

ensure_test_env:
	@for var in HACKBOT_API_KEY SOURCE; do \
		if [ -z "$$var" ]; then \
			echo "$(RED)🚩$$var is not set. Please set $$var before proceeding.$(RESET)"; \
			exit 1; \
		fi \
	done

# Test with live server, taking argument SOURCE as the source directory
test-live: install_dev_deps ensure_test_env
	@$(PYTHON) -m hackbot run -q --source $(SOURCE)

test-local: install_dev_deps ensure_test_env
	@HACKBOT_PORT=$(LOCAL_PORT) HACKBOT_ADDRESS=$(LOCAL_ADDR) $(PYTHON) -m hackbot run -q --source $(SOURCE)



########################################################
# Formatting
########################################################
IGNORE_FORMAT_DIRS= venv .venv .pytest_cache
IGNORE_FORMAT_REGEX= $(shell echo $(IGNORE_FORMAT_DIRS) | sed 's/ /|/g')
.PHONY: format
format: install_dev_deps
	@$(PYTHON) -m black src/ tests/ --line-length 100 --exclude '$(IGNORE_FORMAT_REGEX)'

.PHONY: lint
lint: install_dev_deps format
	@$(PYTHON) -m ruff check src/ tests/ --extend-exclude '/($(IGNORE_LINT_REGEX))/'

.PHONY: lint-fix
lint-fix: install_dev_deps format
	@$(PYTHON) -m ruff check src/ tests/ --extend-exclude '/($(IGNORE_LINT_REGEX))/' --fix

########################################################
# Build and publish to pypi
########################################################
clean_dist:
	rm -rf dist

build_dist: install_dev_deps clean_dist
	rye build

publish: build_dist
	rye build
	rye run python -m twine upload --repository pypi dist/* --verbose

test_publish: build_dist
	rye run python -m twine upload --repository testpypi dist/* --verbose
