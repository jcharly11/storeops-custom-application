#!/bin/bash

IMAGE_NAME='storeops-custom-application'
ARCH=$(dpkg --print-architecture)

if [ $# -eq 1 ]; then
    VERSION=$1
    docker push checkpt/${IMAGE_NAME}:${VERSION}
else
    echo -e "Example: docker-push.sh <VERSION>"
fi
