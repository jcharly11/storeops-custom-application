#!/bin/bash

mosquitto_pub -h 192.168.127.3 -t 'alarm' -m '{"uuid": "13993a0d-4d39-427c-b09f-dea0411b9742", "door_name": "1", "door_number": 1, "store": "1", "serial": "000e26f9df6c9d3", "epc": "E280689400005014CB64F4B6", "hostname": "ckp-e26f9df6c9d3", "extraPayload": {"epc": "E280689400005014CB64F4B6", "event_type": 0, "ip_address": "172.20.30.50:7240", "type": "eas", "timestamp": "2024-02-21 19:19:45.668", "sold": false, "audible_alarm": true, "readcount": "5:0", "tx": "1", "role": "Left PEDESTAL", "disable_light": false, "disable_sound": false}}'
 
