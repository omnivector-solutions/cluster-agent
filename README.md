# armada-agent

# Table of contents

- [Project setup](#project-setup)
  - [Dependencies](#dependencies)
  - [Github secrets](#github-secrets)
- [Setup parameters](#setup-parameters)
- [Local usage example](#local-usage-exemple)
- [Release](#release)
- [Future work](#future-work)

## Project Setup

### Dependencies

* python3-venv

### Github Secrets

* PYPI_URL
* PYPI_USERNAME
* PYPI_PASSWORD

## Setup parameters

1. Setup env
  ```bash
  make dependencies
  ```

2. Setup `.env` parameters
  ```bash
  ARMADA_AGENT_BASE_API_URL="<base-api-url>"
  ARMADA_AGENT_API_KEY="<api-key>"
  ARMADA_AGENT_BASE_SLURMRESTD_URL="<slurmrestd-endpoint>"
  ARMADA_AGENT_X_SLURM_USER_NAME="<slurmrestd-user-name>"
  ARMADA_AGENT_SENTRY_DSN="<sentry-dsn-key>"
  ```

  NOTE: `ARMADA_AGENT_SENTRY_DSN` is optional. If you do not pass it the agent understands Sentry will not be used.

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

Once the pypicloud credentials are set on the repository secrets, pushing a tag will trigger a workflow for pushing the package to pypicloud and releasing on the repository as well. Example:

```bash
git tag -a <version> -m "some message" # e.g. git tag -a 1.0.0 -m "Release"

git push origin <version> # e.g. git push origin 1.0.0
```

NOTE: the workflow won't be triggered if the commit message preceding the tag release contains `release-skip` statement. e.g. `git commit -m "some description here - release-skip"`

## Future work

- [x] Implement script to push package to pypicloud