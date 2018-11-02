import pandas as pd
from tqdm import tqdm
import shapely
import skyfield
import numpy as np
from datetime import datetime, timedelta

# Define types
DataFrame = pd.DataFrame
EarthSatellite = skyfield.api.EarthSatellite


def ground_path(satellite:EarthSatellite, date_from:datetime, date_to:datetime, freq:int=60) -> DataFrame:
    """
    Calculates ground path of a satellite

    Parameters
    ----------
    satellite : EarthSatellite
    date_from : datetime
    date_to : datetime
    freq : int, default 60

    Returns
    ----------
    df : DataFrame
    """

    # Build time array
    td = (date_to - date_from)
    seconds = date_from.second + np.arange(0, td.total_seconds(), freq)
    ts = skyfield.api.load.timescale()
    time_array = ts.utc(year=date_from.year, 
                        month=date_from.month, 
                        day=date_from.day, 
                        hour=date_from.hour, 
                        minute=date_from.minute, 
                        second=seconds)

    # Perform EarthSatellite.at() orbit propagation
    sat_propagated = satellite.at(time_array)

    # Get GCRS Position in km
    position_gcrs = sat_propagated.position.km

    # Get lat lon position
    subpoint = sat_propagated.subpoint()
    lat = subpoint.latitude.degrees
    lon = subpoint.longitude.degrees
    elevation = subpoint.elevation.km

    # Convert to DataFrame
    df = pd.DataFrame({
        'datetime': time_array.utc_datetime(),
        'X': position_gcrs[0],
        'Y': position_gcrs[1],
        'Z': position_gcrs[2],
        'lat': lat,
        'lon': lon,
        'elevation': elevation
    })
    df.set_index('datetime', inplace=True)
    
    # Mark ascending and descending nodes
    df['ascending'] = (df['lat'] >= 0) & (df['lat'].shift(-1).fillna(0) >= 0)
    
    # Calculate orbit
    # (increment every time the satellite crosses equator on ascending node)
    df['orbit'] = (df['ascending'].astype(int).diff() == 1).cumsum()

    return df


def get_nodes(df: DataFrame) -> DataFrame:
    """
    Extracts ascending and descending nodes from ground path

    Parameters
    ----------
    df : DataFrame

    Returns
    ----------
    df_nodes : DataFrame
    """
    mask = (df['ascending'].astype(int).diff()).abs() == True
    df_nodes = df[mask].copy()
    
    return df_nodes


def ltan(df: DataFrame) -> DataFrame:
    """
    Calculates MLTAN (Local Time at Ascending Node)
    
    Parameters
    ----------
    df : DataFrame

    Returns
    ----------
    df_ltan : DataFrame
    """
    df_nodes = get_nodes(df)
    df_ltan = df_nodes[df_nodes['ascending'] == True].copy()

    for idx, row in df_ltan.iterrows():
        h = (row['lon'] * 24) / 360
        
        # calculate local time by subtracting the difference from UTC+0
        local_datetime = idx.replace(tzinfo=None) + timedelta(hours=h)
        local_time = timedelta(hours=local_datetime.hour, 
                               minutes=local_datetime.minute, 
                               seconds=local_datetime.second,
                               microseconds=local_datetime.microsecond) 
        df_ltan.loc[idx, 'local_time'] = local_time
        
    return df_ltan