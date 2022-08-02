# cluster-agent

# Table of contents

- [Project setup](#project-setup)
  - [Dependencies](#dependencies)
- [Install the package](#install-the-package)
- [Setup parameters](#setup-parameters)
- [Local usage example](#local-usage-exemple)

## Project Setup

### Dependencies

* python3-venv

## Install the package

To install the package from Pypi simply run `pip install ovs-cluster-agent`.

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
  CLUSTER_AGENT_OIDC_DOMAIN="<OIDC-domain>"
  CLUSTER_AGENT_OIDC_AUDIENCE="<OIDC-audience>"
  CLUSTER_AGENT_OIDC_CLIENT_ID="<OIDC-app-client-id>"
  CLUSTER_AGENT_OIDC_CLIENT_SECRET="<OIDC-app-client-secret>"
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
