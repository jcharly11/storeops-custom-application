#!/bin/bash

export LPP_URL="http://localhost:8002"
export MQTT_SERVER="127.0.0.1"
export LOG_LEVEL="INFO"

uvicorn main:app --host localhost --port 8005
