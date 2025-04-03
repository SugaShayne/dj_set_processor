"""
Configuration for the YouTube Compatibility Checker module.
"""

# YouTube API configuration
YOUTUBE_API_CONFIG = {
    # API key for YouTube Data API
    # In production, this would be loaded from environment variables
    "api_key": "YOUR_API_KEY",
    
    # YouTube Data API version
    "api_version": "v3",
    
    # API service name
    "api_service_name": "youtube",
    
    # Maximum number of results to return per API call
    "max_results": 5,
    
    # Default region code for content restriction checking
    # This can be overridden when calling the API
    "default_region_code": "US"
}

# Search configuration
SEARCH_CONFIG = {
    # Maximum number of search results to check per track
    "max_videos_to_check": 3,
    
    # Search query format (placeholders: {artist}, {title})
    "query_format": "{artist} {title} official",
    
    # Alternative search query format if first search yields no results
    "alt_query_format": "{title} {artist}"
}

# Content restriction types to check for
RESTRICTION_TYPES = [
    "regionRestriction",  # Geographic restrictions
    "contentRating",      # Age or content-based restrictions
    "privacyStatus"       # Privacy status (private, unlisted, public)
]

# Status codes for compatibility results
STATUS_CODES = {
    "AVAILABLE": "available",       # Content is available
    "BLOCKED": "blocked",           # Content is blocked
    "RESTRICTED": "restricted",     # Content is restricted in some regions
    "UNKNOWN": "unknown"            # Status could not be determined
}

# Cache settings
CACHE_CONFIG = {
    # Whether to cache results
    "enable_cache": True,
    
    # Cache expiration time in seconds (default: 7 days)
    "cache_expiration": 7 * 24 * 60 * 60,
    
    # Cache file path
    "cache_file": "youtube_compatibility_cache.json"
}
