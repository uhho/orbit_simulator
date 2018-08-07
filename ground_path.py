import pandas as pd
from tqdm import tqdm
import shapely
from skyfield.api import load

def ground_path(satellite, date_from, date_to, freq='1min'):

    ts = load.timescale()
    
    dates = pd.date_range(date_from, date_to, freq=freq)

    data = []
    orbit = 0
    prev_lng = None

    for d in tqdm(dates):
        t = ts.utc(d.year, d.month, d.day, d.hour, d.minute, d.second)
        geocentric = satellite.at(t)
        X, Y, Z = geocentric.position.km

        subpoint = geocentric.subpoint()
        elevation = subpoint.elevation.km
        lng = subpoint.longitude.degrees
        lat = subpoint.latitude.degrees
        
        # orbit number
        if prev_lng is not None and lng > prev_lng:
            orbit += 1
        prev_lng = lng

        data.append([d, elevation, lng, lat, orbit, X, Y, Z])
        
    df = pd.DataFrame(data, columns=['datetime', 'elevation', 'lon', 'lat', 'orbit', 'X', 'Y', 'Z'])
    df.set_index('datetime', inplace=True)

    return df