# emissions.py
from geopy.distance import geodesic

def calculate_distance_km(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

def estimate_emission(distance_km, mode='train'):
    factors = {
        'train': 0.05,
        'bus': 0.08,
        'subway': 0.06,
        'tram': 0.04
    }
    return distance_km * factors.get(mode, 0.06)
