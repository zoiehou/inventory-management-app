from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .db import SessionLocal, engine


# Create tables automatically if not using Alembic migrations
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Management API")

# Dependency to get a database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Welcome to the Inventory Management API"}

@app.get("/parts/", response_model=list[schemas.Part])
def read_parts(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    return crud.get_parts(db, skip=skip, limit=limit)

@app.post("/parts/")
def create_part(part: schemas.PartCreate, force: bool = Query(False), db: Session = Depends(get_db)):
    result = crud.create_part(db, part, force)

    # --- normalize keys ---
    duplicates = result.get("duplicates", [])

    if duplicates and not force:
        return {
            "message": "Potential duplicates found.",
            "duplicates": [
                {
                    "part_number": d.part_number,
                    "name": d.name,
                    "manufacturer": d.manufacturer,
                    "category": d.category,
                    "supplier": d.supplier,
                    "sku": d.sku,
                }
                for d in duplicates
            ],
        }

    created = result.get("created")
    return {
        "message": "Part created successfully.",
        "created": {
            "part_number": created.part_number,
            "name": created.name,
        } if created else None,
        "duplicates": [],
    }


@app.get("/locations/", response_model=list[schemas.Location])
def read_locations(db: Session = Depends(get_db)):
    return crud.get_locations(db)

@app.post("/locations/", response_model=schemas.Location)
def create_location(loc: schemas.LocationCreate, db: Session = Depends(get_db)):
    return crud.create_location(db, loc)

@app.post("/inventory/", response_model=schemas.Inventory)
def create_inventory(inventory: schemas.InventoryCreate, db: Session = Depends(get_db)):
    return crud.create_inventory(db, inventory)

@app.post("/inventory/adjust/")
def update_inventory(adjustment: schemas.InventoryAdjustment, db: Session = Depends(get_db)):
    try:
        inventory = crud.adjust_inventory(
            db,
            adjustment.part_id,
            adjustment.location_id,
            adjustment.quantity_change,
            adjustment.version,  # <-- pass version
        )
        return {
            "message": (
                f"Quantity for part_id={adjustment.part_id}, location_id={adjustment.location_id} "
                f"adjusted successfully (new version {inventory.version})"
            ),
            "inventory": {
                "part_id": inventory.part_id,
                "location_id": inventory.location_id,
                "quantity": inventory.quantity,
                "version": inventory.version,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/inventory/move/")
def move_inventory(move: schemas.InventoryMove, db: Session = Depends(get_db)):
    try:
        result = crud.move_inventory(db, move.part_id, move.location_id, move.to_location_id, move.quantity)
        return {
            "message": f"Moved {move.quantity} units of part {move.part_id} from location {move.location_id} to {move.to_location_id}",

            "result": {
                "from": {
                    "location_id": move.location_id,
                    "remaining": result["from"].quantity
                },
                "to": {
                    "location_id": move.to_location_id,
                    "new_total": result["to"].quantity
                }
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/full inventory", response_model=list[schemas.InventoryFull])
def get_full_inventory(db: Session = Depends(get_db)):
    data = crud.get_full_inventory(db)
    return data

@app.get("/inventory aggregated", response_model=list[schemas.InventoryAggregated])
def get_aggregated_inventory(db: Session = Depends(get_db)):
    data = crud.get_aggregated_inventory(db)
    return data