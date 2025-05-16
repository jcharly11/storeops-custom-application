#!/bin/bash
cp -a /app/ui/* /app/cockpit
cp -a /app/visualizer/* /app/cockpit-visualizer
while :
do
    source /app/environment/local-environment-vars.txt
    uvicorn main:app --host 0.0.0.0 --port 80 --log-config /app/log.ini
done
