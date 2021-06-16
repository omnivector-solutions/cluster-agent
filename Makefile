dependencies: ## Install project dependencies needed to run the application
	python3 -m venv env
	. env/bin/activate
	pip3 install -U pip wheel
	pip3 install -r requirements.txt

.PHONY: lint
lint: ## Run flake8 linter. It will checks syntax errors or undefined names
	. env/bin/activate
	flake8 $(git ls-files | grep 'ˆscripts\|\.py$') --count --select=E9,F63,F7,F82 --show-source --statistics

.PHONY: version
version: ## Create/update VERSION file
	@git describe --tags > VERSION

.PHONY: autopep
autopep: ## Run autopep8
	. env/bin/activate
	autopep8 --in-place $(git ls-files | grep 'ˆscripts\|\.py$')

.PHONY: clean
clean: clean-eggs clean-build## Remove temporary file holding the app settings
	rm .env
	rm VERSION
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

.PHONY: run
run: version ## Start uvicorn app on port 8080
	. env/bin/activate
	uvicorn \
		--host 127.0.0.1 \
		--port 8080 \
		armada_agent.main:app --reload

.PHONY: test
test: ## Run tests against the application
	. env/bin/activate
	pytest -v

# Display target comments in 'make help'
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
