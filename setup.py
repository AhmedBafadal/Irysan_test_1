# setup.py
import os
import rasterio
import xarray as xr
from sqlalchemy.orm import Session
from app.database import engine
from app.models import DataEntry, Base  # Import the correct Base

# Load GeoTIFF data and save to SQLite
def load_geotiff_data():
    file_path = "./geotiff_folder/geotiff.tif"
    
    if not os.path.exists(file_path):
        print("GeoTIFF file not found")
        return
    
    try:
        with rasterio.open(file_path) as dataset:
            print("Loading GeoTIFF data into SQLite...")
            with Session(engine) as session:
                for row in range(dataset.height):
                    for col in range(dataset.width):
                        lon, lat = dataset.xy(row, col)
                        pm25_value = dataset.read(1)[row, col]  # Assuming band 1 stores PM2.5

                        # Create a DataEntry object for each row
                        entry = DataEntry(
                            latitude=lat,
                            longitude=lon,
                            year=2023,  # Replace with correct year if available
                            pm25=pm25_value
                        )
                        session.add(entry)
                session.commit()
            print("GeoTIFF data loaded successfully.")
    except Exception as e:
        print(f"Error loading GeoTIFF data: {e}")

# Load netCDF data and save to SQLite
def load_netcdf_data():
    file_path = "./netcdf_folder/netcdf.nc"

    if not os.path.exists(file_path):
        print("netCDF file not found")
        return

    try:
        ds = xr.open_dataset(file_path)
        print("Loading netCDF data into SQLite...")
        with Session(engine) as session:
            lats = ds["lat"].values
            lons = ds["lon"].values
            pm25_values = ds["GWRPM25"].values  # Assuming PM2.5 is stored here

            for i, lat in enumerate(lats):
                for j, lon in enumerate(lons):
                    pm25_value = pm25_values[i, j]

                    # Create a DataEntry object for each row
                    entry = DataEntry(
                        latitude=lat,
                        longitude=lon,
                        year=2023,  # Replace with correct year if available
                        pm25=pm25_value
                    )
                    session.add(entry)
            session.commit()
        print("netCDF data loaded successfully.")
    except Exception as e:
        print(f"Error loading netCDF data: {e}")

# Main function to set up the database
def setup_database():
    print("Setting up the database...")

    # Create database tables
    Base.metadata.create_all(engine)  # Use Base for table creation

    # Load data from GeoTIFF and netCDF files
    load_geotiff_data()
    load_netcdf_data()

    print("Database setup complete.")


if __name__ == "__main__":
    setup_database()
