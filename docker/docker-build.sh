#!/bin/bash

IMAGE_NAME='<APPLICATION_ID>'
ARCH=$(dpkg --print-architecture)

if [ $# -eq 1 ]; then
    VERSION=$1
    cd ..; docker build -t checkpt/${IMAGE_NAME}:${VERSION} -f Dockerfile .; cd -
else
    echo -e "Example: docker-build.sh <VERSION>"
fi
