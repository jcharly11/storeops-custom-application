#!/bin/bash

VERSION="v0.0.1"
HUB_NAME="ckp-prod-europe"
DEPLOYMENT_NAME_PREFIX="storeops-custom-application"
MODULE_CONTENT="modules-content.json"
PRIORITY=$(az iot edge deployment list --hub-name ${HUB_NAME} --query "reverse(sort_by([?starts_with(id, '${DEPLOYMENT_NAME_PREFIX}')].{priority:priority}, &priority))[0]" | jq .priority)
[ -z "${PRIORITY}" ] && PRIORITY=0
PRIORITY=$((PRIORITY + 1))
TARGET_CONDITION="tags.accountId='4500'"
SERVER_URL="http://sfero-test-server"
SERVER_RESPONSE_TOLERANCE_MS=200
SERVER_USERNAME="ckp"
SERVER_PASSWORD="test"
DEPLOYMENT_NAME="${DEPLOYMENT_NAME_PREFIX}-${PRIORITY}"
ALARM_DELAYED_SOUND_ENABLE=0
ALARM_DELAYED_SOUND_VOLUME=0
ALARM_DELAYED_LIGHT_ENABLE=1
ALARM_DELAYED_LIGHT_COLOR="blue"
LOG_LEVEL="INFO"

while getopts v:c:u:t:s:m:l:r:a:p:f: flag
do
    case "${flag}" in
        v) VERSION=${OPTARG};;
        c) TARGET_CONDITION=${OPTARG};;
        u) SERVER_URL=${OPTARG};;
        t) SERVER_RESPONSE_TOLERANCE_MS=${OPTARG};;
        s) ALARM_DELAYED_SOUND_ENABLE=${OPTARG};;
        m) ALARM_DELAYED_SOUND_VOLUME=${OPTARG};;
        l) ALARM_DELAYED_LIGHT_ENABLE=${OPTARG};;
        r) ALARM_DELAYED_LIGHT_COLOR=${OPTARG};;
        a) SERVER_USERNAME=${OPTARG};;
        p) SERVER_PASSWORD=${OPTARG};;
        f) LOG_LEVEL=${OPTARG};;
    esac
done

cp "${MODULE_CONTENT}.template" "${MODULE_CONTENT}"
sed -i "s|<VERSION>|${VERSION}|g" "${MODULE_CONTENT}"
sed -i "s|<SERVER_URL>|${SERVER_URL}|g" "${MODULE_CONTENT}"
sed -i "s|<SERVER_RESPONSE_TOLERANCE_MS>|${SERVER_RESPONSE_TOLERANCE_MS}|g" "${MODULE_CONTENT}"
sed -i "s|<ALARM_DELAYED_SOUND_ENABLE>|${ALARM_DELAYED_SOUND_ENABLE}|g" "${MODULE_CONTENT}"
sed -i "s|<ALARM_DELAYED_SOUND_VOLUME>|${ALARM_DELAYED_SOUND_VOLUME}|g" "${MODULE_CONTENT}"
sed -i "s|<ALARM_DELAYED_LIGHT_ENABLE>|${ALARM_DELAYED_LIGHT_ENABLE}|g" "${MODULE_CONTENT}"
sed -i "s|<ALARM_DELAYED_LIGHT_COLOR>|${ALARM_DELAYED_LIGHT_COLOR}|g" "${MODULE_CONTENT}"
sed -i "s|<SERVER_USERNAME>|${SERVER_USERNAME}|g" "${MODULE_CONTENT}"
sed -i "s|<SERVER_PASSWORD>|${SERVER_PASSWORD}|g" "${MODULE_CONTENT}"
sed -i "s|<LOG_LEVEL>|${LOG_LEVEL}|g" "${MODULE_CONTENT}"

az iot edge deployment create \
    --deployment-id $DEPLOYMENT_NAME \
    --hub-name $HUB_NAME \
    --content $MODULE_CONTENT \
    --target-condition $TARGET_CONDITION \
    --priority $PRIORITY
