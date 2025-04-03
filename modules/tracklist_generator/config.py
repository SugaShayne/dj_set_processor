"""
Configuration for the Tracklist Generator module.
"""

# Database configuration for Dejavu
DATABASE_CONFIG = {
    "database": {
        "host": "127.0.0.1",
        "user": "root",
        "password": "password",  # This would be replaced with environment variables in production
        "database": "dejavu_db",
    },
    "database_type": "mysql"
}

# Audio fingerprinting configuration
FINGERPRINTING_CONFIG = {
    # Maximum length of audio to fingerprint (in seconds)
    # -1 means fingerprint the entire file
    "fingerprint_limit": -1,
    
    # Number of processes to use for parallel fingerprinting
    "processes": 4,
    
    # Minimum amplitude to identify as a peak
    "amp_min": 10,
    
    # Number of cells around an amplitude peak
    "peak_neighborhood_size": 20,
    
    # Degree to which a fingerprint can be paired with its neighbors
    "fan_value": 15,
    
    # Minimum amplitude ratio for peaks to be considered
    "min_amplitude": 10,
    
    # Minimum number of points in a fingerprint to be considered
    "min_points": 5
}

# File formats supported for fingerprinting
SUPPORTED_FORMATS = [".mp3", ".wav", ".flac", ".m4a", ".aac"]

# Confidence threshold for track identification
CONFIDENCE_THRESHOLD = 0.15
