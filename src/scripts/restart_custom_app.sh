#!/bin/bash

mosquitto_pub -t 'command/request/custom/refresh-environment' -m '{"restart": 1}'