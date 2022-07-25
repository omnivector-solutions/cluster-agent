dependencies: ## Install project dependencies needed to run the application
	pip3 install -U pip wheel
	pip3 install -e .[dev]

.PHONY: lint
lint: ## Run flake8 linter
	tox -e lint

.PHONY: clean
clean: clean-eggs clean-build ## Remove temporary file holding the app settings
	rm .env
	rm -rf env/
	find . -iname '*.pyc' -delete
	find . -iname '*.pyo' -delete
	find . -iname '*~' -delete
	find . -iname '*.swp' -delete
	find . -iname '__pycache__' -delete

.PHONY: clean-eggs
clean-eggs: ## Clean eggs
	find . -name '*.egg' -delete
	rm -rf .eggs/

.PHONY: clean-build
clean-build: ## Clean build folders
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

.PHONY: test
test: ## Run tests against the application
	tox -e unit

# Display target comments in 'make help'
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
