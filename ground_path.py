import pandas as pd
from tqdm import tqdm
import shapely
from skyfield.api import load
import numpy as np


def ground_path(satellite, date_from, date_to, freq=60):
    
    # Build time array
    td = (date_to - date_from)
    seconds = date_from.second + np.arange(0, td.total_seconds(), freq)
    ts = load.timescale()
    time_array = ts.utc(year=date_from.year, month=date_from.month, day=date_from.day, 
                        hour=date_from.hour, minute=date_from.minute, second=seconds)

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