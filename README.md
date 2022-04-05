# cluster-agent

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

To get the `PYPI_URL` run `aws codeartifact get-repository-endpoint --domain private --repository cluster-agent --format pypi`

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
  CLUSTER_AGENT_BASE_API_URL="<base-api-url>"
  CLUSTER_AGENT_BASE_SLURMRESTD_URL="<slurmrestd-endpoint>"
  CLUSTER_AGENT_X_SLURM_USER_NAME="<slurmrestd-user-name>"
  CLUSTER_AGENT_SENTRY_DSN="<sentry-dsn-key>"
  CLUSTER_AGENT_AUTH0_DOMAIN="<auth0-domain>"
  CLUSTER_AGENT_AUTH0_AUDIENCE="<auth0-audience>"
  CLUSTER_AGENT_AUTH0_CLIENT_ID="<auth0-app-client-id>"
  CLUSTER_AGENT_AUTH0_CLIENT_SECRET="<auth0-app-client-secret>"
  CLUSTER_AGENT_LDAP_HOST="<hostname-for-ldap>"
  CLUSTER_AGENT_LDAP_DOMAIN="<LDAP-domain>" # Defaults to match LDAP_HOST
  CLUSTER_AGENT_LDAP_USERNAME="<admin-user>"
  CLUSTER_AGENT_LDAP_PASSWORD="<admin-password>"
  ```

  NOTE: `CLUSTER_AGENT_SENTRY_DSN` is optional. If you do not pass it the agent understands Sentry will not be used.

## Local usage example

1. Run app
  ```bash
  agentrun
  ```

**Note**: this command assumes you're inside a virtual environment in which the package is installed.

**NOTE**: beware you should care about having the same user name you're using to run the code in the slurmctld node. For example, if `cluster_agent` will run the `make run` command then the slurmctld node also must have a user called `cluster_agent`.

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

pip3 install cluster-agent==<version> -i https://aws:$CODEARTIFACT_AUTH_TOKEN@private-<aws account id>.d.codeartifact.<aws region>.amazonaws.com/pypi/cluster-agent/simple/
```
