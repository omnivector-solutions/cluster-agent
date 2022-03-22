#!/bin/bash

host=$(hostname)
sed -i "s/REPLACE_HOST/$host/g" /etc/slurm/slurm.conf
sed -i "s/REPLACE_HOST/$host/g" /etc/slurm/slurmdbd.conf

service munge start
service slurmctld start
service slurmdbd start

export SLURMRESTD_SECURITY=disable_unshare_sysv
slurmrestd -vvvv -s openapi/v0.0.36 -a rest_auth/local 0.0.0.0:6820

tail -f /dev/null
