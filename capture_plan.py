from datetime import datetime, timedelta
from functools import reduce
from typing import Union

import numpy as np
from skyfield.api import EarthSatellite, load, Time, Topos
from skyfield.constants import AU_M
import pandas as pd
import pyproj

import time_utils
import vector_utils

# Define types
DataFrame = pd.DataFrame
Num = Union[int, float]
ndarray = np.ndarray
TimeRange = time_utils.TimeRange


def capture_plan(satellite: EarthSatellite, target_lat: Num, target_lon: Num, 
                 target_altitude: Num, date_from: datetime, date_to: datetime, freq: Num = 5, 
                 min_off_nadir_angle: Num = 0, max_off_nadir_angle: Num = 20, 
                 min_solar_zenith_angle: Num = 0, max_solar_zenith_angle: Num = 60,
                 local_time_range: TimeRange = time_utils.time_range(
                     start_times = [timedelta(hours=0, minutes=0, seconds=0, microseconds=0)],
                     end_times = [timedelta(hours=24, minutes=0, seconds=0, microseconds=0)]
                 )) -> DataFrame:
    """Calculates capturable date and condition
    
    Parameters
    ---------
    satellite : EarthSatellite
    date_from : datetime
    date_to : datetime
    freq: int or float, default 5
    min_off_nadir_angle: int or flaot, default 0
    max_off_nadir_angle: int or flaot, default 20
    min_solar_zenith_angle: int or flaot, default 0
    max_solar_zenith_angle: int or flaot, default 60
    local_time_range: time_utils.TimeRange.
        It can be set by using time_utils.time_range function.
        default is all day (from 00:00:00 to 24:00:00).
    """
    
    # Calculate satellite off-nadir angles
    time_array = time_utils.build_time_array(date_from, date_to, freq)
    target_position = _lla_to_ecef(target_lat, target_lon, target_altitude)
    satellite_positions_au, _, _ = satellite.ITRF_position_velocity_error(time_array)
    satellite_positions = satellite_positions_au.T * AU_M
    off_nadir_angles = np.array([vector_utils.calc_off_nadir_angle(sp, target_position)[2] for sp in satellite_positions])
    with np.errstate(invalid='ignore'):                                  
        available_idx = np.where((off_nadir_angles >= min_off_nadir_angle) & (off_nadir_angles <= max_off_nadir_angle))
    off_nadir_angles = off_nadir_angles[available_idx]

    if len(available_idx[0]) == 0:
        return pd.DataFrame(
            index=['datetime'],
            columns=['off_nadir_angle', 'solar_zenith_angle', 'local_time']
        )

    # Calculate solar zenith angles
    time_array = Time(time_array.ts, time_array.tt[available_idx])
    planets = load('de421.bsp')
    sun = planets['sun']
    earth = planets['earth']
    lat_symbol = 'N' if target_lat >= 0 else 'S'
    lon_symbol = 'E' if target_lon >= 0 else 'W'
    target_area = earth + Topos(
        '{} {}'.format(abs(target_lat), lat_symbol),
        '{} {}'.format(abs(target_lon), lon_symbol), 
        elevation_m=target_altitude)
    apparent = target_area.at(time_array).observe(sun).apparent()
    alt, az, distance = apparent.altaz()
    solar_zenith_angles = 90 - alt.degrees
    
    df = pd.DataFrame({
        'datetime': time_array.utc_datetime(),
        'off_nadir_angle': off_nadir_angles,
        'solar_zenith_angle': solar_zenith_angles,
    })
    df['local_time'] = [time_utils.calc_local_time(dt, target_lon) for dt in df.datetime]

    df = df[
        (df.solar_zenith_angle >= min_solar_zenith_angle) & 
        (df.solar_zenith_angle <= max_solar_zenith_angle)].set_index('datetime')

    if len(local_time_range.time_pairs) > 0:
        df = df[reduce(
            lambda a, b: a | b,
            [(df.local_time >= pair[0]) & (df.local_time <= pair[1]) for pair in local_time_range.time_pairs]
        )]

    return df

def _lla_to_ecef(lat: Num, lon: Num, alt: Num) -> ndarray:
    """
    Convert lla (latitude, longitude, altitude) into ECEF coordinate.

    Parameters
    ---------
    lat : int or float
    lon : int or float
    alt : int or float
    """
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    x, y, z = pyproj.transform(lla, ecef, lon, lat, alt, radians=False)
    return np.array([x, y, z])
