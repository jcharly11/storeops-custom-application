#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <application_id> <application_name>"
    exit 1;
fi

APPLICATION_ID=$1
APPLICATION_NAME=$2

# Install the required packages
sudo apt update -qy
sudo apt install python3-dev python3-venv mosquitto mosquitto-clients -qy

# Change directory names
[ -d pkg/APPLICATION_ID ] && mv pkg/APPLICATION_ID pkg/${APPLICATION_ID}

# Change file names
[ -f pkg/${APPLICATION_ID}/etc/systemd/system/APPLICATION_ID.service ] \
&& mv pkg/${APPLICATION_ID}/etc/systemd/system/APPLICATION_ID.service pkg/${APPLICATION_ID}/etc/systemd/system/${APPLICATION_ID}.service

# Change file contents
sed -i "s/<APPLICATION_ID>/${APPLICATION_ID}/g" .gitignore
sed -i "s/<APPLICATION_NAME>/${APPLICATION_NAME}/g" .gitignore

sed -i "s/<APPLICATION_ID>/${APPLICATION_ID}/g" README.md
sed -i "s/<APPLICATION_NAME>/${APPLICATION_NAME}/g" README.md

for f in ./.github/workflows/* ./docker/* ./iotedge/*; do
    sed -i "s/<APPLICATION_ID>/${APPLICATION_ID}/g" "${f}"
    sed -i "s/<APPLICATION_NAME>/${APPLICATION_NAME}/g" "${f}"
done;

for f in ./pkg/*.sh ./pkg/${APPLICATION_ID}/DEBIAN/* ./pkg/${APPLICATION_ID}/etc/systemd/system/${APPLICATION_ID}.service; do
    sed -i "s/<APPLICATION_ID>/${APPLICATION_ID}/g" "${f}"
    sed -i "s/<APPLICATION_NAME>/${APPLICATION_NAME}/g" "${f}"
done;

sed -i "s/<APPLICATION_ID>/${APPLICATION_ID}/g" src/ui/files.js
sed -i "s/<APPLICATION_ID>/${APPLICATION_ID}/g" src/ui/index.js
sed -i "s/<APPLICATION_ID>/${APPLICATION_ID}/g" src/ui/setup.sh
