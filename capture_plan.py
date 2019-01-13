from datetime import datetime, timedelta
from functools import reduce
from typing import Tuple, Union

import numpy as np
import skyfield
from skyfield.api import EarthSatellite, load, Time, Topos
from skyfield.constants import AU_M
import pandas as pd
import pyproj

import time_utils

# Define types
DataFrame = pd.DataFrame
Num = Union[int, float]
ndarray = np.ndarray
float64 = np.float64
Time = skyfield.timelib.Time
TimeRange = time_utils.TimeRange


def capture_plan(satellite: EarthSatellite, target_lat: Num, target_lon: Num, 
                 target_altitude: Num, date_from: datetime, date_to: datetime, freq: Num = 5, 
                 min_off_nadir_angle: Num = 0, max_off_nadir_angle: Num = 20, 
                 min_satellite_elevation_angle: Num = 0, max_satellite_elevation_angle: Num = 90, 
                 min_solar_elevation_angle: Num = 30, max_solar_elevation_angle: Num = 90,
                 local_time_range: TimeRange = time_utils.time_range(
                     start_times = [timedelta(hours=0, minutes=0, seconds=0, microseconds=0)],
                     end_times = [timedelta(hours=24, minutes=0, seconds=0, microseconds=0)]
                 )) -> DataFrame:
    """Calculates capturable date and condition
    
    Parameters
    ---------
    satellite : EarthSatellite
    target_lat: int or float
    target_lon: int or float
    target_altitude: int or float
    date_from : datetime
    date_to : datetime
    freq: int or float, default 5
    min_off_nadir_angle: int or flaot, default 0
    max_off_nadir_angle: int or flaot, default 20
    min_satellite_elevation_angle: int or flaot, default 0
    max_satellite_elevation_angle: int or flaot, default 90
    min_solar_elevation_angle: int or flaot, default 30
    max_solar_elevation_angle: int or flaot, default 90
    local_time_range: time_utils.TimeRange.
        It can be set by using time_utils.time_range function.
        default is all day (from 00:00:00 to 24:00:00).
    """

    time_array = time_utils.build_time_array(date_from, date_to, freq)
    off_nadir_angles, satellite_elevation_angles = calc_satellite_angles(
        satellite, target_lat, target_lon, target_altitude, time_array
    )
    available_idx = np.where(
        (off_nadir_angles >= min_off_nadir_angle) & \
        (off_nadir_angles <= max_off_nadir_angle) & \
        (satellite_elevation_angles >= min_satellite_elevation_angle) & \
        (satellite_elevation_angles <= max_satellite_elevation_angle)
    )
    off_nadir_angles = off_nadir_angles[available_idx]
    satellite_elevation_angles = satellite_elevation_angles[available_idx]

    if len(available_idx[0]) == 0:
        return pd.DataFrame(
            index=['datetime'],
            columns=['off_nadir_angle', 'satellite_elevation_angle', 'solar_elevation_angle', 'local_time']
        )

    time_array = Time(time_array.ts, time_array.tt[available_idx])
    solar_elevation_angles = calc_solar_elevation_angles(
        target_lat, target_lon, target_altitude, time_array
    )

    df = pd.DataFrame({
        'datetime': time_array.utc_datetime(),
        'off_nadir_angle': off_nadir_angles,
        'satellite_elevation_angle': satellite_elevation_angles,
        'solar_elevation_angle': solar_elevation_angles,
    })
    df['local_time'] = [time_utils.calc_local_time(dt, target_lon) for dt in df.datetime]

    df = df[
        (df.solar_elevation_angle >= min_solar_elevation_angle) & 
        (df.solar_elevation_angle <= max_solar_elevation_angle)].set_index('datetime')

    if len(local_time_range.time_pairs) > 0:
        df = df[reduce(
            lambda a, b: a | b,
            [(df.local_time >= pair[0]) & (df.local_time <= pair[1]) for pair in local_time_range.time_pairs]
        )]

    return df

def calc_satellite_angles(satellite: EarthSatellite, target_lat: Num, target_lon: Num, 
                           target_altitude: Num, time_array: Time) -> Tuple[ndarray, ndarray]:
    """Calculates satellite off-nadir and elevation angles
    
    Parameters
    ---------
    satellite : EarthSatellite
    target_lat: int or float
    target_lon: int or float
    target_altitude: int or float
    time_array: Time
    """
    satellite_positions_au, _, _ = satellite.ITRF_position_velocity_error(time_array)
    satellite_positions = satellite_positions_au.T * AU_M
    target_position = _lla_to_ecef(target_lat, target_lon, target_altitude)
    target_position = np.broadcast_to(target_position, satellite_positions.shape)
    los_vectors = target_position - satellite_positions
    off_nadir_angles = _angle_between(los_vectors, -satellite_positions, axis=1)
    satellite_elevation_angles = 90 - _angle_between(los_vectors, -target_position, axis=1) # 90 - satellite_zenith_angles
    return off_nadir_angles, satellite_elevation_angles

def calc_solar_elevation_angles(target_lat: Num, target_lon: Num, 
                                 target_altitude: Num, time_array: Time) -> ndarray:
    """Calculates solar elevation angles
    
    Parameters
    ---------
    target_lat: int or float
    target_lon: int or float
    target_altitude: int or float
    time_array: Time
    """
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
    solar_elevation_angles = alt.degrees
    return solar_elevation_angles

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

def _unit_vector(vector: ndarray, axis: int = 1) -> ndarray:
    """
    Calculate unit vector

    Parameters
    ---------
    vector : ndarray
    axis : int
    """
    return vector / np.expand_dims(np.linalg.norm(vector, axis=axis), axis=axis)

def _angle_between(v1: ndarray, v2: ndarray, axis: int = 1) -> float64:
    """
    Calculate angle [degree] between two vectors

    Parameters
    ---------
    v1 : ndarray
    v2 : ndarray
    axis : int
    """
    v1_u = _unit_vector(v1, axis)
    v2_u = _unit_vector(v2, axis)
    angle = np.rad2deg(np.arccos(np.clip(np.sum(v1_u * v2_u, axis=axis), -1.0, 1.0)))
    return angle
