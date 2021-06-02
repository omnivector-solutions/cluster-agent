dependencies: pyproject.toml ## Install project dependencies needed to run the application
	virtualenv -p python3 env
	. env/bin/activate \
		&& pip3 install -U pip wheel poetry \
		&& python3 -m pip install .[dev] \
		&& pip3 freeze | grep -v armada-agent > requirements.txt

.PHONY: lint
lint: ## Run flake8 linter. It will checks syntax errors or undefined names
	flake8 $(git ls-files | grep 'ˆscripts\|\.py$') --count --select=E9,F63,F7,F82 --show-source --statistics

.PHONY: autopep
autopep: ## Run autopep8
	autopep8 --in-place $(git ls-files | grep 'ˆscripts\|\.py$')

.PHONY: clean
clean: ## Remove temporary file holding the app settings
	rm .env
	rm -rf dist/

.PHONY: run
run: ## Start uvicorn app on port 8080
	poetry run uvicorn \
		--host 127.0.0.1 \
		--port 8080 \
		armada_agent.main:app --reload

.PHONY: test
test: ## Run tests against the application
	poetry run pytest -v

.PHONY: publish
publish: clean ## Publish package to pypicloud
	. env/bin/activate
	poetry build

	poetry config repositories.pypicloud ${PYPI_URL}

	poetry publish \
		--repository pypicloud \
		--username ${PYPI_USERNAME} \
		--password ${PYPI_PASSWORD}

# Display target comments in 'make help'
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'