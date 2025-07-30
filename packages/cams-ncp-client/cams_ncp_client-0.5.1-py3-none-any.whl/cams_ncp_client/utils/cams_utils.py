
from datetime import date, datetime
from pathlib import Path

import pandas as pd


def get_station_concentrations(df_stations: pd.DataFrame, cams_nc_file: Path, base_date: date, cams_var: str, method="nearest") -> pd.DataFrame:
    """
    Get concentrations (in the cams_nc-file) for all stations in df_stations for the given date.
    The stations in df_stations must have columns 'name', 'lat', 'lon'.
    The cams_nc_file must be a netcdf file with dimensions (time, latitude, longitude) and a variable named cams_var.
    The base_date is used to create the timestamp index for the resulting DataFrame.
    The method parameter specifies how to select the nearest grid point for each station (default is "nearest").

    Args:
        df_stations (pd.DataFrame): DataFrame containing station information with columns 'name', 'lat', 'lon'. (Cfr: StationClient.find_stations_df())
        cams_nc_file (Path): Path to the netcdf file containing CAMS data. (Cfr: CamsFileClient.download_cams_file())
        base_date (date): Base date for the timestamps in the resulting DataFrame.
        cams_var (str): Variable name in the netcdf file to extract concentrations.
        method (str): Method to select nearest grid point ('nearest' or 'pad'). Default is 'nearest'.

    Returns:
        A DataFrame with timestamps as index and station names as columns, containing the concentrations for each station.
    """
    import xarray as xr
    with xr.open_dataset(cams_nc_file, engine="h5netcdf", decode_timedelta=False) as ds:
        conc_ds = ds[cams_var].isel(level=0)  # Dimensions: (time, latitude, longitude)

        # Prepare coordinates as DataArrays with 'station' dimension
        station_names = df_stations["name"].values
        lats = xr.DataArray(df_stations["lat"].values, dims=["station"])
        lons = xr.DataArray(df_stations["lon"].values, dims=["station"])

        # Get nearest grid values for all stations
        station_data = conc_ds.sel(latitude=lats, longitude=lons, method=method)  # Dimensions: (station, time)

        base_time = pd.Timestamp(datetime.combine(base_date, datetime.min.time()), tz="UTC")

        result_df = station_data.to_pandas()
        result_df.columns = station_names

        hour_values = result_df.index.get_level_values(0)
        new_timestamps = pd.to_timedelta(hour_values, unit="h") + base_time

        # Reset index and set new timestamp index
        result_df = result_df.reset_index()
        result_df.index = new_timestamps
        result_df.index.name = "timestamp"
        return result_df