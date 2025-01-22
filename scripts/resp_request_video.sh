#!/bin/bash

mosquitto_pub -t 'command_resp/onvif/video/get_video' -m '{"header": {"timestamp": "2024-09-13T16:16:45.944-05:00", "uuid_request": "0000000-0000000-000000002000", "version": "1.0.0"}, "data": {"status": "OK", "destination_path": "./videos/0000000-0000000-000000002000XX/", "file_name": "0000000-0000000-000000002000.mp4"}}'
