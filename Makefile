dependencies: pyproject.toml ## Install project dependencies needed to run the application
	virtualenv -p python3 env
	. env/bin/activate \
		&& pip3 install -U pip wheel poetry \
		&& python3 -m pip install .[dev] \
		&& pip3 freeze | grep -v armada-agent > requirements.txt

lint: ## Run flake8 linter. It will checks syntax errors or undefined names
	flake8 $(git ls-files | grep 'ˆscripts\|\.py$') --count --select=E9,F63,F7,F82 --show-source --statistics

autopep: ## Run autopep8
	autopep8 --in-place $(git ls-files | grep 'ˆscripts\|\.py$')

clean: ## Remove temporary file holding the app settings
	rm /tmp/.env

run: ## Start uvicorn app on port 8080
	poetry run uvicorn \
		--host 127.0.0.1 \
		--port 8080 \
		armada_agent.main:app --reload

test: ## Run tests against the application
	poetry run pytest -v

# Display target comments in 'make help'
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'