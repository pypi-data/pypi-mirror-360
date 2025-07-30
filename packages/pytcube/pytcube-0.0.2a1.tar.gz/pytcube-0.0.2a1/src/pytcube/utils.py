import numpy as np

EARTH_CIRCUMFERENCE_IN_DEG = 360
EARTH_CIRCUMFERENCE_IN_KM = 40_070

def km2deg(km):
    """Convert a distance from kilometers to degrees."""
    return (km * EARTH_CIRCUMFERENCE_IN_DEG) / EARTH_CIRCUMFERENCE_IN_KM

def deg2km(deg):
    """Convert a distance from degrees to kilometers."""
    return (deg * EARTH_CIRCUMFERENCE_IN_KM) / EARTH_CIRCUMFERENCE_IN_DEG

def nano2min(nano):
    """Convert time from nanoseconds to minutes."""
    return nano / np.timedelta64(1, 'm')

def find_nearest_indices(coord_array: np.ndarray, obs_array: np.ndarray) -> np.ndarray:
    """Find nearest indexes of obs in coords array"""

    # Trouver les indices d'insertion
    idx = np.searchsorted(coord_array, obs_array)
    
    # Assurer que les indices sont dans les limites
    idx = np.clip(idx, 1, len(coord_array)-1)
    
    # Comparer les valeurs avant et après l'index trouvé
    left = coord_array[idx - 1]
    right = coord_array[idx]
    
    # Trouver quel côté est le plus proche
    idx_nearest = idx - (obs_array - left < right - obs_array)

    return idx_nearest