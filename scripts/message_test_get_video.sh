#!/bin/bash

mosquitto_pub -h '192.168.127.3' -t 'command_resp/onvif/video/get-video' -m '{ "requester_id": "0000-0000-0000-0000","uuid": "0000-0000-0000-0000","message_id": "00000", "timestamp": "12/12/2024", "data": "[]"}'