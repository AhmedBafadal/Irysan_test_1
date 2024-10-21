# app/utils.py
import pandas as pd
import xarray as xr
import rioxarray

# Load netCDF to Pandas DataFrame
def load_netcdf_to_dataframe(file_path: str) -> pd.DataFrame:
    ds = xr.open_dataset(file_path)
    df = ds.to_dataframe().reset_index()
    return df[['latitude', 'longitude', 'year', 'PM2.5']]

# Load GeoTIFF to Pandas DataFrame
def load_geotiff_to_dataframe(file_path: str) -> pd.DataFrame:
    da = rioxarray.open_rasterio(file_path)
    df = da.to_dataframe().reset_index()
    return df[['latitude', 'longitude', 'year', 'PM2.5']]