=========
Changelog
=========

This file keeps track of all notable changes to the Armada agent.

Unreleased
----------

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