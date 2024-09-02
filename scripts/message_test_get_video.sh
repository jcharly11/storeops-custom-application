#!/bin/bash

mosquitto_pub  -t 'command_resp/onvif/video/get-video' -m '{ "requester_id": "0000-0000-0000-0000","uuid": "0000-0000-0000-0000","message_id": "00000", "timestamp": "12/12/2024", "data": "[]"}'