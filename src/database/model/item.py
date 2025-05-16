from dataclasses import dataclass


@dataclass
class Item:
    sku: str
    epc: str
    description: str
    image: str