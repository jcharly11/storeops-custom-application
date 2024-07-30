import uuid
from datetime import datetime

STANDARD_PAYLOAD = "{{type: {type}, \
                    uuid: {uuid}, \
                    message_id: {message_id}, \
                    uuid_request: {uuid_request}, \
                    timestamp:{timestamp}, \
                    version: {version} \
                    data: {data}}}"


type = "STOREOPS_MESSAGE_EVENT"
uuid = uuid.uuid4()
message_id = "Only applies for event/status messages."
uuid_request = "Only applies for response messages"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
version = "1.0"
data = [{
        "key1" : "hello", 
        "key2": "world"}]

payload = STANDARD_PAYLOAD.format(
    type = type,
    uuid = uuid,
    uuid_request = uuid_request,
    message_id = message_id,
    timestamp = timestamp,
    version = version,
    data = data
)

print(payload)