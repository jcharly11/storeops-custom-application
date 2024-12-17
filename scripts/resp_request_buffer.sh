#!/bin/bash

mosquitto_pub -t 'command_resp/onvif/image/get_buffer' -m '{"header": {"timestamp": "2024-09-13T16:16:24.287-05:00", "uuid_request": "0000000-0000000-000000002000XX", "version": "1.0.0"}, "data": {"status": "OK", "destination_path": "./snapshots/0000000-0000000-000000002000XX", "image_number": "6"}}'
