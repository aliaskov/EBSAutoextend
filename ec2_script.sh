#!/bin/bash
instanceid=`curl -s http://instance-data/latest/meta-data/instance-id`
echo "Hello World from $instanceid"
