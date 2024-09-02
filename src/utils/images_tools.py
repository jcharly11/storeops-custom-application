import base64
import logging

class ImageEncoder:
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def encodeBytes(self, data):
        try:
            base64Bytes= base64.b64encode(data) 
            return base64Bytes.decode()

        except Exception as ex:
            self.logger.error(f"Error encoding image from bytes: {ex}")

    def encodeImage(self, path):
        try:
             with open(path, "rb") as image:
                videoB64 = base64.b64encode(image.read())
             return videoB64.__str__() 

        except Exception as ex:
            self.logger.error(f"Error encoding image frm file: {ex}")

            