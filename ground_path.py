import geopandas as gpd
from tqdm import tqdm
import shapely
from skyfield.api import load

def ground_path(satellite, date_from, date_to, freq='1min'):

    ts = load.timescale()
    
    dates = gpd.pd.date_range(date_from, date_to, freq=freq)

    data = []
    orbit = 0
    prev_lng = None

    for d in tqdm(dates):
        t = ts.utc(d.year, d.month, d.day, d.hour, d.minute, d.second)
        geocentric = satellite.at(t)

        subpoint = geocentric.subpoint()
        elevation = subpoint.elevation.km
        lng = subpoint.longitude.degrees
        lat = subpoint.latitude.degrees
        p = shapely.geometry.Point(lng, lat)

        # orbit number
        if prev_lng is not None and lng > prev_lng:
            orbit += 1
        prev_lng = lng

        data.append([d, elevation, lng, lat, orbit, p])
        
    df = gpd.GeoDataFrame(data, columns=['datetime', 'elevation', 'lon', 'lat', 'orbit', 'geometry'], crs={'init': 'epsg:4326'})
    df['orbit'] = df['orbit'].astype('category')
    df.set_index('datetime', inplace=True)

    return df