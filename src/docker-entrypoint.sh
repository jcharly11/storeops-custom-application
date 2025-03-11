#!/bin/bash

cp -a /app/ui/* /app/cockpit
cp -a /app/scripts/* /app/shell-scripts
cp -a /app/ssl/* /app/certificates
while :
do
    if [ -f /app/etc/timezone ]; then
        echo "File not found!"
        TIMEZONE_FILE="/usr/share/zoneinfo/"`cat /app/etc/timezone`
        if [ -f $TIMEZONE_FILE ]; then
            ln -sf $TIMEZONE_FILE /etc/localtime
        fi
    fi


    source /app/environment/local-environment-vars.txt
    source /app/environment/ui-local-environment-vars.txt
    groupadd cockpit-ui-permissions
    usermod -a -G cockpit-ui-permissions service
    usermod -a -G cockpit-ui-permissions checkpoint
    chgrp -R cockpit-ui-permissions /app/environment/
    chmod -R 770 /app/environment/
    uvicorn main:app --host 127.0.0.1 --port 80 --log-config /app/log.ini
done


