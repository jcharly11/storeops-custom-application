#!/bin/bash

mosquitto_pub -h '192.168.127.3' -t 'checkpoint/EMPTY/EMPTY/service/command_resp/onvif/image/snapshot' -m '{"header":{"timestamp": "2024/05/27","uuid_request": "0000-1111-1111-1111","version": "1.0.0"},"data": {"status": "OK","image": "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAABDSURBVChTlYpBDgAgCMP4/6eRYFGMkmAvy9aJNvg/SYLJ2QWZQKwT8wWWCN6VCN6VKMDOMJgTiHwykA6Tc5SKxkl1ANaEHvDuvggsAAAAAElFTkSuQmCC"}}'

