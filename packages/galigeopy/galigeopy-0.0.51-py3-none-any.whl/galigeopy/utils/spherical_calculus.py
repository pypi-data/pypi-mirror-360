# Haversine distance formula
from math import asin, cos, radians, sin, sqrt, pi
import numpy as np

def haversine_distance(lat1, lon1, lat2, lon2, rayon=6371000)->list|float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lat1 = np.array(lat1) * pi / 180
    lon1 = np.array(lon1) * pi / 180
    lat2 = np.array(lat2) * pi / 180
    lon2 = np.array(lon2) * pi / 180
    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.asin(np.sqrt(a))
    km = rayon * c
    return km