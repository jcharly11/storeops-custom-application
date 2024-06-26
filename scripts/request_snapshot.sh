#!/bin/bash
mosquitto_pub -t 'command/onvif/image/snapshot' -m  '{"header":{"uuid_request":"0000-0000-0000-0000"},"snapshot" : true}'