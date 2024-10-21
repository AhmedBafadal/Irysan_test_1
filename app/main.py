# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import rasterio
import xarray as xr
from . import models, schemas
from .database import engine, get_db, SessionLocal  # Import SessionLocal from the database module


# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Load data from GeoTIFF and netCDF files when the app starts
@app.on_event("startup")
def load_data_on_startup():
    load_geotiff_data()
    load_netcdf_data()

def load_geotiff_data():
    file_path = "./geotiff_folder/geotiff.tif"
    
    if not os.path.exists(file_path):
        print("GeoTIFF file not found")
        return
    
    try:
        with rasterio.open(file_path) as dataset:
            print("Loading GeoTIFF data into SQLite...")
            with SessionLocal() as db:
                for row in range(dataset.height):
                    for col in range(dataset.width):
                        lon, lat = dataset.xy(row, col)
                        pm25_value = dataset.read(1)[row, col]  # Assuming PM2.5 values in band 1

                        db_entry = models.DataEntry(
                            latitude=lat,
                            longitude=lon,
                            year=2023,  # Replace with correct year if available
                            pm25=pm25_value
                        )
                        db.add(db_entry)
                db.commit()
                print("GeoTIFF data loaded successfully.")
    except Exception as e:
        print(f"Error loading GeoTIFF data: {e}")

def load_netcdf_data():
    file_path = "./netcdf_folder/netcdf.nc"

    if not os.path.exists(file_path):
        print("netCDF file not found")
        return

    try:
        ds = xr.open_dataset(file_path)
        print("Loading netCDF data into SQLite...")
        with SessionLocal() as db:
            lats = ds["lat"].values
            lons = ds["lon"].values
            pm25_values = ds["GWRPM25"].values  # Assuming PM2.5 values are stored here

            for i, lat in enumerate(lats):
                for j, lon in enumerate(lons):
                    pm25_value = pm25_values[i, j]

                    db_entry = models.DataEntry(
                        latitude=lat,
                        longitude=lon,
                        year=2023,  # Replace with correct year if available
                        pm25=pm25_value
                    )
                    db.add(db_entry)
            db.commit()
            print("netCDF data loaded successfully.")
    except Exception as e:
        print(f"Error loading netCDF data: {e}")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Air Quality API"}

# 1. GET /data: Retrieve all available data
@app.get("/data", response_model=list[schemas.DataEntryResponse])
def get_all_data(db: Session = Depends(get_db)):
    data_entries = db.query(models.DataEntry).all()
    return data_entries

# 2. GET /data/{id}: Retrieve a specific data entry by ID
@app.get("/data/{id}", response_model=schemas.DataEntryResponse)
def get_data_by_id(id: int, db: Session = Depends(get_db)):
    entry = db.query(models.DataEntry).filter(models.DataEntry.id == id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Data entry not found")
    return entry

# 3. POST /data: Add a new data entry
@app.post("/data", response_model=schemas.DataEntryResponse)
def create_data_entry(entry: schemas.DataEntryCreate, db: Session = Depends(get_db)):
    db_entry = models.DataEntry(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

# 4. PUT /data/{id}: Update an existing data entry
@app.put("/data/{id}", response_model=schemas.DataEntryResponse)
def update_data_entry(id: int, entry: schemas.DataEntryCreate, db: Session = Depends(get_db)):
    db_entry = db.query(models.DataEntry).filter(models.DataEntry.id == id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Data entry not found")
    
    for key, value in entry.dict().items():
        setattr(db_entry, key, value)

    db.commit()
    db.refresh(db_entry)
    return db_entry

# 5. DELETE /data/{id}: Delete a specific data entry
@app.delete("/data/{id}")
def delete_data_entry(id: int, db: Session = Depends(get_db)):
    db_entry = db.query(models.DataEntry).filter(models.DataEntry.id == id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Data entry not found")
    db.delete(db_entry)
    db.commit()
    return {"message": f"Data entry {id} deleted successfully"}