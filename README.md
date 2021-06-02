# armada-agent

# Table of contents

- [Project setup](#project-setup)
  - [Github secrets](#github-secrets)
- [Setup parameters](#setup-parameters)
- [Local usage example](#local-usage-exemple)
- [Release](#release)
- [Future work](#future-work)

## Project Setup

### Github Secrets

* PYPI_URL
* PYPI_USERNAME
* PYPI_PASSWORD

## Setup parameters

1. Setup env
  ```bash
  make dependencies
  ```

2. Activate env
  ```bash
  source env/bin/activate
  ```

3. Setup `.env` parameters
  ```bash
  poetry run agentconfig
  ```

## Local usage example

1. Run app
  ```bash
  make run
  ```

Outputs:
  ```bash
  INFO:     Started server process [8798]
  INFO:     Waiting for application startup.
  INFO:     Run collecting
  INFO:     Depends(get_agent)
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
  ```

2. Make local request
  ```bash
  curl http://localhost:8080/health
  ```

Outputs:
  ```json
  {"status":"ok","message":""}
  ```

## Release

For publishing you need first to export some credentials:

```bash
export PYPI_URL="https://link-to-pypicloud.com"
export PYPI_USERNAME="rats"
export PYPI_PASSWORD="ratsratsrats"
```

Then, run:

```bash
make publish
```

## Future work

- [ ] TODO