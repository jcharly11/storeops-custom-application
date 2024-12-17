
class SharepointMessage:
    
    def __init__(self) -> None:
        self.type = None
        self.uuid = None
        self.path = None
        self.files = None
        self.status = None 


class SharepointCreateLinkMessage(SharepointMessage):
    
    def __init__(self) -> None:
        SharepointMessage.__init__(self)
        self.type = 'create_link'
        self.link = None 

    def __getitem__(self, cls):
        return getattr(self, cls)        


class SharepointUploadFilesMessage(SharepointMessage):
    
    def __init__(self) -> None:
        self.type = 'upload'
        self.destination_path = None

    def __getitem__(self, cls):
        return getattr(self, cls)     
