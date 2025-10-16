# Define ORM / Database structure

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from .db import Base

class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    part_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    supplier = Column(String(100), nullable=False)
    sku = Column(String(50), nullable=False)
    description = Column(String(255))

    inventory = relationship("Inventory", back_populates="part")

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    inventory = relationship("Inventory", back_populates="location")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    last_modified = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    version = Column(Integer, default=1)

    part = relationship("Part", back_populates="inventory")
    location = relationship("Location", back_populates="inventory")

