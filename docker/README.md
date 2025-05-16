# Docker Utilities

> The scripts will only run on Linux machines or similar.

## Pre-requisites
1. Install Docker by following the instructions in [Link](https://docs.docker.com/engine/install/).

## Scripts
### docker-build
- Build the docker image that can be pushed to DockerHub repository
```bash
./docker-build.sh v0.0.1
```
### docker-run
- Run a docker container for the specified version of the image.
```bash
./docker-run.sh v0.0.1
```
### docker-stop
- Stop and destroy the docker container.
```bash
./docker-stop.sh
```
### docker-push
- Push the specified version of the docker image to DockerHub repository.
```bash
docker login
./docker-push.sh
```
