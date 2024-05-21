#!/bin/bash

IMAGE_NAME='<APPLICATION_ID>'
ARCH=$(dpkg --print-architecture)

if [ $# -eq 1 ]; then
    VERSION=$1
    docker run -d --name custom-app checkpt/${IMAGE_NAME}:${VERSION}
else
    echo -e "Example: docker-run.sh <VERSION>"
fi
