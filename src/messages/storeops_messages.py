
class StoreOpsMessage:
    
    def __init__(self) -> None:
        self.type = None
        self.uuid = None
        self.timestamp = None
        self.device_model = None
        self.device_id = None
        self.version = None
        self.data = []
        self.send_local = True
        self.send_storeops = True
    def __str__(self):
        return f"type:{self.type},uuid:{self.uuid},timestamp:{self.timestamp},device_model:{self.device_model},device_id:{self.device_id},data:{self.data}"

class EventMessage(StoreOpsMessage):
    
    def __init__(self) -> None:
        StoreOpsMessage.__init__(self)
        self.type = 'event'
        self.technology = None
        self.customer = None
        self.store = None
        self.group = None
        self.event_id = None

class StatusMessage(StoreOpsMessage):
    
    def __init__(self) -> None:
        StoreOpsMessage.__init__(self)
        self.type = 'status'
        self.technology = None
        self.customer = None
        self.store = None
        self.group = None
        self.status_id = None

class ConfigurationMessage(StoreOpsMessage):
    
    def __init__(self) -> None:
        StoreOpsMessage.__init__(self)
        self.type = 'configuration'
        self.technology = None
        self.customer = None
        self.store = None
        self.group = None
        self.configuration_id = None


class CommandMessage(StoreOpsMessage):
    
    def __init__(self) -> None:
        StoreOpsMessage.__init__(self)
        self.type = 'command'
        self.customer = None
        self.store = None
        self.command_id = None
        self.destination = []
        self.expiration_date = None


class InfoMessage(StoreOpsMessage):
    
    def __init__(self) -> None:
        StoreOpsMessage.__init__(self)
        self.type = 'info'
        self.customer = None
        self.store = None
        self.info_id = None
        self.expiration_date = None
        self.uuid_request = None

class ResponseMessage(StoreOpsMessage):
    
    def __init__(self) -> None:
        StoreOpsMessage.__init__(self)
        self.type = 'response'
        self.customer = None
        self.store = None
        self.response_id = None
        self.uuid_request = None

#mensjae enviado a servicio de storeops (ej: command interno (reenvia todo))
class InternalMessage(StoreOpsMessage):
    
    def __init__(self) -> None:
        StoreOpsMessage.__init__(self)
        self.type = 'internal'
        self.command_id = None
