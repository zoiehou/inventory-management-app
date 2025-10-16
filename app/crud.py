from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
from sqlalchemy import func

def get_parts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Part).offset(skip).limit(limit).all()

def check_duplicate_parts(db: Session, part: schemas.PartCreate):
    return (
        db.query(models.Part)
        .filter(
            models.Part.manufacturer == part.manufacturer,
            models.Part.category == part.category,
            models.Part.supplier == part.supplier,
            models.Part.sku == part.sku,
        )
        .all()
    )


def create_part(db: Session, part: schemas.PartCreate, force: bool = False):
    duplicates = check_duplicate_parts(db, part)

    if duplicates and not force:
        return {"duplicates": duplicates, "created": None}

    # --- create new part number ---
    last_part = db.query(models.Part).order_by(models.Part.id.desc()).first()
    next_part_number = 1 if not last_part else last_part.id + 1
    part_number = f"P{next_part_number:05d}"

    part_data = part.dict()
    part_data["part_number"] = part_number

    db_part = models.Part(**part_data)
    db.add(db_part)
    db.commit()
    db.refresh(db_part)

    return {"duplicates": [], "created": db_part}

def delete_part(db: Session, part_id: int):
    db.query(models.Part).filter(models.Part.id == part_id).delete()
    db.commit()


def get_locations(db: Session):
    return db.query(models.Location).all()

def create_location(db: Session, location: schemas.LocationCreate):
    db_location = models.Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def delete_location(db: Session, location_id: int):
    db.query(models.Location).filter(models.Location.id == location_id).delete()
    db.commit()


#def get_inventory(db: Session):
#    return db.query(models.Inventory).all()

def create_inventory(db: Session, inventory: schemas.InventoryCreate):
    # Check if inventory already exists
    current_inventory = (
        db.query(models.Inventory)
        .filter_by(part_id=inventory.part_id, location_id=inventory.location_id)
        .first()
    )

    if current_inventory:
        current_inventory.quantity += inventory.quantity
        current_inventory.version += 1
        current_inventory.last_modified = datetime.now().replace(microsecond=0)
        
    else:
        current_inventory = models.Inventory(**inventory.dict())
        db.add(current_inventory)
    
    db.commit()
    db.refresh(current_inventory)
    return current_inventory


def adjust_inventory(db: Session, part_id: int, location_id: int, quantity_change: int, version: int):
    inventory = (
        db.query(models.Inventory)
        .filter_by(part_id=part_id, location_id=location_id)
        .first()
    )

    if not inventory:
        # If no existing record, allow creating a new one
        new_inventory = models.Inventory(
            part_id=part_id,
            location_id=location_id,
            quantity=quantity_change,
            version=1,
            last_modified=datetime.now().replace(microsecond=0)
        )
        db.add(new_inventory)
        db.commit()
        db.refresh(new_inventory)
        return new_inventory

    # --- Optimistic concurrency check ---
    if version != inventory.version:
        raise ValueError(
            f"Version conflict: expected {inventory.version}, got {version}"
        )

    # --- Safe to update ---
    inventory.quantity += quantity_change
    inventory.version += 1
    inventory.last_modified = datetime.now().replace(microsecond=0)

    db.commit()
    db.refresh(inventory)
    return inventory


def move_inventory(db: Session, part_id: int, from_location_id: int, to_location_id: int, quantity: int):
    # Decrease quantity from source location and increase at destination location
    source = db.query(models.Inventory).filter_by(part_id = part_id, location_id = from_location_id).first()
    if not source or source.quantity < quantity:
        raise ValueError("Insufficient stock at source location")

    source.quantity -= quantity
    source.version += 1

    destination = db.query(models.Inventory).filter_by(part_id = part_id, location_id = to_location_id).first()
    if destination:
        destination.quantity += quantity
        destination.version += 1
    else:
        destination = models.Inventory(part_id = part_id, location_id = to_location_id, quantity = quantity, version = 1)
        db.add(destination)

    db.commit()
    return {"from": source, "to": destination}


def get_full_inventory(db: Session):
    results = (
        db.query(
            models.Part.part_number.label("part_number"),
            models.Part.name.label("part_name"),
            models.Location.name.label("location_name"),
            models.Inventory.quantity,
            models.Part.manufacturer,
            models.Part.category,
            models.Part.supplier,
            models.Part.sku,
            models.Inventory.version,
            models.Inventory.last_modified,
        )
        .join(models.Part, models.Inventory.part_id == models.Part.id)
        .join(models.Location, models.Inventory.location_id == models.Location.id)
        .all()
    )
    return results


def get_aggregated_inventory(db: Session):
    results = (
        db.query(
            models.Part.name.label("part_name"),
            models.Part.manufacturer,
            models.Part.category,
            models.Part.supplier,
            models.Part.sku,
            func.sum(models.Inventory.quantity).label("total_quantity")
        )
        .join(models.Inventory, models.Inventory.part_id == models.Part.id)
        .group_by(
            models.Part.id,
            models.Part.name,
            models.Part.manufacturer,
            models.Part.category,
            models.Part.supplier,
            models.Part.sku
        )
        .all()
    )
    return results