#!/bin/bash

mosquitto_pub -h 192.168.127.3 -t 'store/info' -m '{"uuid": "0000-000-000-0000"}'