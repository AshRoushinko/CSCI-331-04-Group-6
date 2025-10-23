# Hav's formula, used to calculate the distance between two points on earth given lat and long

from math import radians, sin, cos, asin, sqrt

EARTH_RADIUS_MI = 3958.8  # miles


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:

    φ1, λ1, φ2, λ2 = map(radians, [lat1, lon1, lat2, lon2]) # convert degreese to rads ( not sure if greek letters will work t)
    dφ, dλ = (φ2 - φ1), (λ2 - λ1) # calculate the differences
    a = sin(dφ/2)**2 + cos(φ1)*cos(φ2)*sin(dλ/2)**2  # this is 1. Haversine's formula
    c = 2 * asin(sqrt(a)) # calculate  angular distance
    return EARTH_RADIUS_MI * c # convert to miles
