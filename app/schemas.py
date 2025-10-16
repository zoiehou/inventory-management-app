from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PartBase(BaseModel):
    name: str
    manufacturer: str
    category: str
    supplier: str
    sku: str
    description: Optional[str] = None

class PartCreate(PartBase):
    pass

class Part(PartBase):
    id: int
    part_number: str

    class Config:
        from_attributes = True  # allows returning SQLAlchemy models directly


class LocationBase(BaseModel):
    name: str

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    class Config:
        from_attributes = True


class InventoryBase(BaseModel):
    part_id: int
    location_id: int
    
class InventoryCreate(InventoryBase):
    quantity: int

class Inventory(InventoryBase):
    id: int
    quantity: int
    version: int
    last_modified: datetime
    class Config:
        from_attributes = True

class InventoryAdjustment(InventoryBase):
    quantity_change: int
    version: int

class InventoryMove(InventoryBase):
    to_location_id: int
    quantity: int

class InventoryFull(BaseModel):
    part_name: str
    location_name: str
    quantity: int
    manufacturer: str
    category: str
    supplier: str
    sku: str
    version: int
    last_modified: datetime

    class Config:
        from_attributes = True

class InventoryAggregated(BaseModel):
    part_name: str
    total_quantity: int
    manufacturer: str
    category: str
    supplier: str
    sku: str

    class Config:
        from_attributes = True