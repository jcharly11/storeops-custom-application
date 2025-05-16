# IoT Edge Deployment

> WARNING: Azure CLI currently only works on AMD64.

> The scripts will only run on Linux machines or similar.

## Pre-requisites
1. Install Azure CLI by following the instructions in [Link](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt)
2. Log-in to Azure by running the following.
```bash
az login
```

## Deployment
1. Update `modules-content.json.template` if necessary.
2. Update `deploy.sh` parameters.
```
VERSION - version of the checkpt/lpp-custom-application docker image.
PRIORITY - increment the number to deploy this version to all associated devices.
TARGET_CONDITION - change if necessary (eg. deploying to development devices).
```
3. Run the deployment.
```bash
./deploy.sh
```
