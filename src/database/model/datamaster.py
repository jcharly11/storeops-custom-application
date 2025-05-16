from pydantic import BaseModel


class Datamaster(BaseModel):
        sku: str
        epc: str
        description: str
        image: str