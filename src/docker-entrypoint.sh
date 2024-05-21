#!/bin/bash

cp -a /app/ui/* /app/cockpit
cp -a /app/scripts/* /app/shell-scripts
while :
do
    source /app/environment/local-environment-vars.txt
    source /app/environment/ui-local-environment-vars.txt
    uvicorn main:app --host 127.0.0.1 --port 80
done


