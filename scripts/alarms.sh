#!/bin/bash

max=1
for  x in `seq 1 $max`
do
dt=$(date '+%Y-%m-%dT%H:%M:%S.%3N')
uuid=$(python3 -c 'import uuid; print(uuid.uuid4())') 

payload=$(jq -n \
 --arg uuid "$uuid" \
 --arg dt "$dt" \
   '{"uuid": $uuid, "door_name": "1", "door_number": 1, "store": "1", "serial": "000e26f9df6c9d3", "epc": "E280689400005014CB64F4B6", "hostname": "ckp-e26f9df6c9d3","extraPayload": {"epc":"E280689400005014CB64F4B6", "event_type": 0, "ip_address": "172.20.30.50:7240", "type": "eas", "timestamp": $dt , "sold": false, "audible_alarm": true,"readcount":"5:0", "tx": "1", "role": "Left PEDESTAL", "disable_light": false, "disable_sound": false}}')

echo  $uuid
pwd=$(pwd) 
workingfile=$(echo $pwd  | awk '{gsub(/scripts/,"src")}1') 
mosquitto_pub -t 'alarm' -m "$payload"

mkdir "$workingfile/videos/$uuid"
touch "$workingfile/videos/$uuid/$uuid.mp4"
images=5
mkdir "$workingfile/snapshots/$uuid"
images_array=()
for i in `seq 1 $images`
do

touch "$workingfile/snapshots/$uuid/$i.jpg"
 

done
snapshots="./snapshots/$uuid"
videos="./videos/$uuid"
mp4="$uuid.mp4"
echo $snapshots
echo $videos
echo $mp4 
sleep 5

get_buffer=$(jq -n \
 --arg uuid "$uuid" \
 --arg snapshots "$snapshots" \
 '{"header": {"timestamp": "2024-09-13T16:16:24.287-05:00", "uuid_request": $uuid, "version": "1.0.0"}, "data": {"status": "OK", "destination_path": $snapshots, "file_name": ["1.jpg","2.jpg","3.jpg","4.jpg","5.jpg"]}}'
)
mosquitto_pub -t 'command_resp/onvif/image/get_buffer' -m "$get_buffer"

# sleep 5

# get_video=$(jq -n \
#  --arg uuid "$uuid" \
#  --arg videos "$videos" \
#   --arg mp4 "$mp4" \
#  '{"header": {"timestamp": "2024-09-13T16:16:45.944-05:00", "uuid_request": $uuid, "version": "1.0.0"}, "data": {"status": "OK", "destination_path": $videos, "file_name": $mp4}}'
# )
# mosquitto_pub -t 'command_resp/onvif/video/get_video' -m "$get_video" 

# sleep 10
done