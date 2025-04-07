#!/bin/bash 

mosquitto_pub -t 'status/onvif/camera' -m  '{ "header":{ "timestamp":"2025-03-19T13:19:38.912", "version":"1.0.0"}, "data": {"status": "OK","online": true,"ip": "192.168.127.71","port": "80","image_taking_enable": true,"video_recording": true}}'   