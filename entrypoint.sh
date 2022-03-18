#!/bin/bash

while true
do
    echo "Executing agent in loop"
    python3 cluster_agent/main.py
    echo "Sleeping for 15 seconds"
    sleep 15
done
