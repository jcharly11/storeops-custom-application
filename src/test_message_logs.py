from utils.log_message_utils import LogMessagesUtil

message = '{message: examples}'
logMessageUtils = LogMessagesUtil()
if logMessageUtils.create():
    logMessageUtils.save(message=message, storeId=None, customerId=None, doorId=None)



    