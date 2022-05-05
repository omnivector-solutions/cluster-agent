=========
Changelog
=========

This file keeps track of all notable changes to the Cluster Agent.

Unreleased
----------

- Added job-script parser to extract the name and values of the SBATCH parameters contained in the file.
- Added a two-way mapping to translate parameters' names between the SBATCH namespace and the SLURM Rest API namespace.

1.5.0 - 2022-04-12
------------------

- Disabled cluster data collectors.

1.4.0 - 2022-04-07
------------------

- Moved LDAP support into ``slurm_user`` module.
- Made slurm user mapping more extensible.
- Fixed username mapping for NTLM auth type.

1.3.0 - 2022-04-05
------------------

- Added jobbergate section for retrieving, submitting, and updating jobs from Jobbergate
- Added support for looking up usernames from LDAP via email from auth token
- Added unit tests for jobbergate section

1.2.0 - 2022-02-15
------------------

- removed dependency on FastAPI and Uvicorn;
- removed autoscheduling from the agent;
- implemented a function to call sequentially the functions that collect slurmrestd data.

1.1.0 - 2022-01-25
------------------

- implemented logic to authenticate against the Cluster API by Auth0 tokens;
- changed logic to issue Slurmrestd JWT;
- removed *request* module;
- created *identity* module to handle client logics for the APIs (Cluster APi and Slurmrestd).

1.0.0 - 2022-01-19
------------------

- bump project name from *armada-agent*  to *cluster-agent*.

0.2.2 - 2022-01-11
------------------

- fixed backend's partition route.

0.2.1 - 2021-10-19
------------------

- changed the logging stack to use `Loguru`_.

0.2.0 - 2021-10-14
------------------

- changed function to issue slurm JWT token without passing the username explicitly.

0.1.3 - 2021-09-08
------------------

- implemented the core functionalities of the agent: scrape slurmrestd for diagnostics, jobs, partitions and nodes data;
- implemented GitHub workflows for testing and linting the code, as well as publishing it to AWS CodeArtifact.

.. _Loguru: https://pypi.org/project/loguru/
