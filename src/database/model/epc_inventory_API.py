class EPC_Inventory_API():

    def __init__(self,epc,timestamp,alarm_type,description,image,sku):
        self.epc= epc
        self.timestamp = timestamp
        self.alarm_type = alarm_type
        self.description = description
        self.image= image
        self.sku= sku