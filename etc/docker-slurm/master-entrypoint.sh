#!/bin/bash

export SLURM_CPUS_ON_NODE=$(cat /proc/cpuinfo | grep processor | wc -l)
sed -i "s/REPLACE_IT/CPUs=${SLURM_CPUS_ON_NODE}/g" /etc/slurm-llnl/slurm.conf

service munge start
service slurmctld start

tail -f /dev/null
