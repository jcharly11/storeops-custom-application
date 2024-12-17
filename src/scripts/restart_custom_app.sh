#!/bin/bash

mosquitto_pub -t 'command/request/custom/storeops-custom-application/refresh-environment' -m '{"restart": 1}'
