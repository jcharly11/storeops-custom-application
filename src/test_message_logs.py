from utils.log_message_utils import LogMessagesUtil
import json
message = json.loads("'message':{ 'data': 'None'}") 
logMessageUtils = LogMessagesUtil()
if logMessageUtils.create():
    logMessageUtils.save(message=message, storeId=None, customerId=None, doorId=None, topic="test")



    