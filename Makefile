dependencies: ## Install project dependencies needed to run the application
	python3 -m venv env
	. env/bin/activate
	pip3 install -U pip wheel
	pip3 install -r requirements.txt

.PHONY: lint
lint: ## Run flake8 linter. It will checks syntax errors or undefined names
	flake8 $(git ls-files | grep 'ˆscripts\|\.py$') --count --select=E9,F63,F7,F82 --show-source --statistics

.PHONY: version
version: ## Create/update VERSION file
	@git describe --tags > VERSION

.PHONY: autopep
autopep: ## Run autopep8
	autopep8 --in-place $(git ls-files | grep 'ˆscripts\|\.py$')

.PHONY: clean
clean: ## Remove temporary file holding the app settings
	rm .env
	rm -rf dist/

.PHONY: run
run: version ## Start uvicorn app on port 8080
	. env/bin/activate
	uvicorn \
		--host 127.0.0.1 \
		--port 8080 \
		armada_agent.main:app --reload

.PHONY: test
test: version ## Run tests against the application
	. env/bin/activate
	pytest -v

# Display target comments in 'make help'
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'