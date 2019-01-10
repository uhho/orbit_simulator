from typing import Sequence, Tuple

import numpy as np

# Define types
ndarray = np.ndarray
float64 = np.float64


def unit_vector(vector: ndarray) -> ndarray:
    """
    Calculate unit vector

    Parameters
    ---------
    vector : ndarray
    """
    return vector / np.linalg.norm(vector)

def angle_between(v1: ndarray, v2: ndarray) -> float64:
    """
    Calculate angle [degree] between two vectors

    Parameters
    ---------
    v1 : ndarray
    v2 : ndarray
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.rad2deg(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))

def los_to_earth(satellite_position: Sequence[float], los_unit_vec: Sequence[float], 
                 polar_radius: float = 6371008.7714, equatorial_radius: float = 6356752.314245) -> Tuple[bool, ndarray, ndarray]:
    """
    Calculate intersection between line of sight of satellite and Earth.

    Parameters
    ---------
    satellite_position : Sequence[float] (x, y, z)
    los_unit_vec : Sequence[float] (x, y, z), 
        This is unit vector of line of sight.
    polar_radius : float, default 6371008.7714 
        Default value is based on 
        National Imagery and Mapping Agency Technical Report TR 8350.2 Third Edition,
        Amendment 1, 1 Jan 2000, "Department of Defense World Geodetic System 1984"
    equatorial_radius : float, default 6356752.314245
        Default value is based on 
        National Imagery and Mapping Agency Technical Report TR 8350.2 Third Edition,
        Amendment 1, 1 Jan 2000, "Department of Defense World Geodetic System 1984"
    """
    # See following reference for polar and equatorial radius: National Imagery and Mapping Agency Technical Report TR 8350.2 Third Edition, Amendment 1, 1 Jan 2000, "Department of Defense World Geodetic System 1984"
    a = polar_radius
    b = polar_radius
    c = equatorial_radius
    x = satellite_position[0]
    y = satellite_position[1]
    z = satellite_position[2]
    u = los_unit_vec[0]
    v = los_unit_vec[1]
    w = los_unit_vec[2]

    value = -a**2*b**2*w*z - a**2*c**2*v*y - b**2*c**2*u*x
    radical = a**2*b**2*w**2 + a**2*c**2*v**2 - a**2*v**2*z**2 + 2*a**2*v*w*y*z - a**2*w**2*y**2 + b**2*c**2*u**2 - b**2*u**2*z**2 + 2*b**2*u*w*x*z - b**2*w**2*x**2 - c**2*u**2*y**2 + 2*c**2*u*v*x*y - c**2*v**2*x**2
    magnitude = a**2*b**2*w**2 + a**2*c**2*v**2 + b**2*c**2*u**2

    if radical < 0:
        # The Line-of-Sight vector does not point toward the Earth
        exist_intersection = False
        p1 = np.nan
        p2 = np.nan
        return exist_intersection, p1, p2
    
    d1 = (value - a*b*c*np.sqrt(radical)) / magnitude
    d2 = (value + a*b*c*np.sqrt(radical)) / magnitude

    if d1 < 0:
        # The Line-of-Sight vector does not point toward the Earth
        exist_intersection = False
        p1 = np.nan
        p2 = np.nan
        return exist_intersection, p1, p2
    
    exist_intersection = True
    p1 = satellite_position + d1 * los_unit_vec # Near side of the earth
    p2 = satellite_position + d2 * los_unit_vec # Far side of the earth
    return exist_intersection, p1, p2

def calc_off_nadir_angle(satellite_position: Sequence[float], target_position: Sequence[float], 
                         polar_radius: float = 6371008.7714, equatorial_radius: float = 6356752.314245) -> Tuple[bool, bool, float64]:
    """
    Calculate satellite off-nadir angle [degree]

    Parameters
    ---------
    satellite_position : Sequence[float] (x, y, z)
    target_position : Sequence[float] (x, y, z)
    polar_radius : float, default 6371008.7714 
        Default value is based on 
        National Imagery and Mapping Agency Technical Report TR 8350.2 Third Edition,
        Amendment 1, 1 Jan 2000, "Department of Defense World Geodetic System 1984"
    equatorial_radius : float, default 6356752.314245
        Default value is based on 
        National Imagery and Mapping Agency Technical Report TR 8350.2 Third Edition,
        Amendment 1, 1 Jan 2000, "Department of Defense World Geodetic System 1984"
    """
    los_vec = target_position - satellite_position
    los_unit_vec = unit_vector(los_vec)
    exist_intersection, near_side_p, far_side_p = los_to_earth(satellite_position, los_unit_vec, polar_radius, equatorial_radius)
    
    if exist_intersection:
        if np.linalg.norm(near_side_p - target_position) <= np.linalg.norm(far_side_p - target_position):
            near_side = True
        else:
            near_side = False
    else:
        near_side = None
        
    if near_side:
        off_nadir_angle = angle_between(-satellite_position, los_vec)
    else:
        off_nadir_angle = np.nan
    
    return exist_intersection, near_side, off_nadir_angle
