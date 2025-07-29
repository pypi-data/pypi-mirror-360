.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@uv run mypy
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry src

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

.PHONY: publish
publish: ## Publish a release to PyPI.
	@echo "🚀 Publishing."
	@uvx twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

.PHONY: build-exe
build-exe: ## Build standalone executable (fast-starting folder mode)
	@echo "🚀 Building standalone executable (fast 'dir' mode)"
	@uv run python build.py --mode=dir

.PHONY: build-exe-dist
build-exe-dist: ## Build single-file distributable executable (slow startup)
	@echo "🚀 Building distributable single-file executable ('file' mode)"
	@uv run python build.py --mode=file

.PHONY: clean-exe
clean-exe: ## Clean executable build artifacts
	@echo "🚀 Cleaning executable build artifacts"
	@uv run python -c "import shutil; from pathlib import Path; [shutil.rmtree(p) for p in (Path('build'), Path('dist')) if p.exists()]"

.PHONY: test-exe
test-exe: build-exe ## Build and test the executable
	@echo "🚀 Testing executable"
	@if [ -f "dist/pyinstaller/SimpleTimerBank.exe" ]; then echo "✅ Executable built successfully: dist/pyinstaller/SimpleTimerBank.exe"; else echo "❌ Executable not found"; exit 1; fi

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: publish-docs
publish-docs: ## Build and publish the documentation to GitHub Pages
	@echo "🚀 Building and deploying documentation to GitHub Pages"
	@uv run mkdocs gh-deploy --clean

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile, encoding='utf-8').read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
