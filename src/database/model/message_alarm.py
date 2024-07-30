class MessageAlarm():

    def __init__(self,
                 request_uuid,
                 message,
                 status,
                 type,
                 datetime_inserted):


        self.request_uuid = request_uuid
        self.message= message
        self.status= status
        self.type= type
        self.datetime_inserted = datetime_inserted