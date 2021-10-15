# armada-agent

# Table of contents

- [Project setup](#project-setup)
  - [Github secrets](#github-secrets)
  - [Dependencies](#dependencies)
- [Setup parameters](#setup-parameters)
- [Local usage example](#local-usage-exemple)
- [Release](#release)
- [Install the package](#install-the-package)

## Project Setup

### Github Secrets

* PYPI_URL
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY_ID

**NOTE**: AWS keys must have the `codeartifact:PublishPackageVersion` and `codeartifact:GetRepositoryEndpoint` permissions on resource identified by the `PYPI_URL`.

To get the `PYPI_URL` run `aws codeartifact get-repository-endpoint --domain private --repository armada-agent --format pypi`

### Dependencies

* python3-venv
* AWS CLI (>= 2.1.10)

Configure the aws credentials running `aws configure`. To know which permissions do you must have check the [github secrets](#github-secrets) section.

## Setup parameters

1. Setup dependencies
  You can use whenever dependency manager you want to. Just run the command below (and the ones following) on behalf of the manager you prefer.

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

**NOTE**: beware you should care about having the same user name you're using to run the code in the slurmctld node. For example, if `armada_agent` will run the `make run` command then the slurmctld node also must have a user called `armada_agent`.

2. Make local request
  ```bash
  curl http://localhost:8080/health
  ```

Outputs:
  ```json
  {"status":"ok","message":""}
  ```

## Release

There is a GitHub action to publish the package to the codeartifact repository. Trigger it manually hence a GitHub release will also be created.

## Install the package

Before trying to install make sure your IAM user has the following permissions:

* `codeartifact:GetAuthorizationToken`
* `codeartifact:GetRepositoryEndpoint`
* `codeartifact:ReadFromRepository`

**NOTE**: if you're planning to install the package on codebuild make sure codebuild also has the `sts:GetServiceBearerToken` permission.

Then, run:

```bash
CODEARTIFACT_AUTH_TOKEN=`aws codeartifact get-authorization-token --domain private --query authorizationToken --output text`

pip3 install armada-agent==<version> -i https://aws:$CODEARTIFACT_AUTH_TOKEN@private-<aws account id>.d.codeartifact.<aws region>.amazonaws.com/pypi/armada-agent/simple/
```
