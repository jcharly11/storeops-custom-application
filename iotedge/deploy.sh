#!/bin/bash

VERSION="v0.0.1"
HUB_NAME="ckp-prod-europe"
DEPLOYMENT_NAME_PREFIX="storeops-basic-custom-application"
MODULE_CONTENT="modules-content.json"
PRIORITY=$(az iot edge deployment list --hub-name ${HUB_NAME} --query "reverse(sort_by([?starts_with(id, '${DEPLOYMENT_NAME_PREFIX}')].{priority:priority}, &priority))[0]" | jq .priority)
[ -z "${PRIORITY}" ] && PRIORITY=0
PRIORITY=$((PRIORITY + 1))
TARGET_CONDITION="tags.accountId='4500'"
HOST_SFTP="sftp-storeops.checkpoint-service.com"
PORT_SFTP=22
USERNAME_SFTP="wirama2"
PASSWORD_SFTP="F69tvbQ8f7fK"
DEPLOYMENT_NAME="${DEPLOYMENT_NAME_PREFIX}-${PRIORITY}"
SHEDULE_CREATE_CSV_FILES=1800
CREATE_CSV_FILES_ENABLE=1
ALARM_AGGREGATION_WINDOW_SEC=1.0
LOG_LEVEL="INFO"


while getopts v:c:u:t:a:p:i:g:r:f: flag
do
    case "${flag}" in
        v) VERSION=${OPTARG};;
        c) TARGET_CONDITION=${OPTARG};;
        u) HOST_SFTP=${OPTARG};;
        t) PORT_SFTP=${OPTARG};;
        a) USERNAME_SFTP=${OPTARG};;
        p) PASSWORD_SFTP=${OPTARG};;
        i) SHEDULE_CREATE_CSV_FILES=${OPTARG};;
        g) CREATE_CSV_FILES_ENABLE=${OPTARG};;
        r) ALARM_AGGREGATION_WINDOW_SEC==${OPTARG};;
        f) LOG_LEVEL=${OPTARG};;
    esac
done

cp "${MODULE_CONTENT}.template" "${MODULE_CONTENT}"
sed -i "s|<VERSION>|${VERSION}|g" "${MODULE_CONTENT}"
sed -i "s|<HOST_SFTP>|${HOST_SFTP}|g" "${MODULE_CONTENT}"
sed -i "s|<PORT_SFTP>|${PORT_SFTP}|g" "${MODULE_CONTENT}"
sed -i "s|<USERNAME_SFTP>|${USERNAME_SFTP}|g" "${MODULE_CONTENT}"
sed -i "s|<PASSWORD_SFTP>|${PASSWORD_SFTP}|g" "${MODULE_CONTENT}"
sed -i "s|<SHEDULE_CREATE_CSV_FILES>|${SHEDULE_CREATE_CSV_FILES}|g" "${MODULE_CONTENT}"
sed -i "s|<CREATE_CSV_FILES_ENABLE>|${CREATE_CSV_FILES_ENABLE}|g" "${MODULE_CONTENT}"
sed -i "s|<ALARM_AGGREGATION_WINDOW_SEC>|${ALARM_AGGREGATION_WINDOW_SEC}|g" "${MODULE_CONTENT}"
sed -i "s|<LOG_LEVEL>|${LOG_LEVEL}|g" "${MODULE_CONTENT}"

az iot edge deployment create \
    --deployment-id $DEPLOYMENT_NAME \
    --hub-name $HUB_NAME \
    --content $MODULE_CONTENT \
    --target-condition $TARGET_CONDITION \
    --priority $PRIORITY
