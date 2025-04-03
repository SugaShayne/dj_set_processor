"""
Core functionality for the YouTube Compatibility Checker module.
"""

import os
import json
import time
import logging
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import (
    YOUTUBE_API_CONFIG, 
    SEARCH_CONFIG, 
    RESTRICTION_TYPES, 
    STATUS_CODES,
    CACHE_CONFIG
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('youtube_checker')

class YouTubeCompatibilityChecker:
    """
    Class for checking YouTube compatibility of tracks.
    """
    
    def __init__(self, api_key=None, cache_dir=None):
        """
        Initialize the YouTubeCompatibilityChecker.
        
        Args:
            api_key: YouTube Data API key (overrides config)
            cache_dir: Directory to store cache files
        """
        self.api_key = api_key or YOUTUBE_API_CONFIG["api_key"]
        self.cache_dir = cache_dir
        self.cache = {}
        
        # Initialize YouTube API client
        self.youtube = build(
            YOUTUBE_API_CONFIG["api_service_name"],
            YOUTUBE_API_CONFIG["api_version"],
            developerKey=self.api_key
        )
        
        # Load cache if enabled
        if CACHE_CONFIG["enable_cache"]:
            self._load_cache()
    
    def _load_cache(self):
        """
        Load cache from file.
        """
        cache_path = self._get_cache_path()
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                    # Filter out expired cache entries
                    current_time = time.time()
                    self.cache = {
                        k: v for k, v in cache_data.items()
                        if v.get("expiration", 0) > current_time
                    }
                logger.info(f"Loaded {len(self.cache)} cache entries from {cache_path}")
            except Exception as e:
                logger.error(f"Error loading cache: {str(e)}")
                self.cache = {}
    
    def _save_cache(self):
        """
        Save cache to file.
        """
        if not CACHE_CONFIG["enable_cache"]:
            return
            
        cache_path = self._get_cache_path()
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            with open(cache_path, 'w') as f:
                json.dump(self.cache, f, indent=2)
            logger.info(f"Saved {len(self.cache)} cache entries to {cache_path}")
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
    
    def _get_cache_path(self):
        """
        Get the path to the cache file.
        
        Returns:
            Path to the cache file
        """
        if self.cache_dir:
            return os.path.join(self.cache_dir, CACHE_CONFIG["cache_file"])
        else:
            return CACHE_CONFIG["cache_file"]
    
    def _get_cache_key(self, artist, title):
        """
        Generate a cache key for a track.
        
        Args:
            artist: Artist name
            title: Track title
            
        Returns:
            Cache key string
        """
        return f"{artist.lower()}:{title.lower()}"
    
    def _add_to_cache(self, artist, title, result):
        """
        Add a result to the cache.
        
        Args:
            artist: Artist name
            title: Track title
            result: Result to cache
        """
        if not CACHE_CONFIG["enable_cache"]:
            return
            
        cache_key = self._get_cache_key(artist, title)
        expiration = time.time() + CACHE_CONFIG["cache_expiration"]
        
        self.cache[cache_key] = {
            "result": result,
            "expiration": expiration,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save cache periodically
        if len(self.cache) % 10 == 0:
            self._save_cache()
    
    def _get_from_cache(self, artist, title):
        """
        Get a result from the cache.
        
        Args:
            artist: Artist name
            title: Track title
            
        Returns:
            Cached result or None if not found
        """
        if not CACHE_CONFIG["enable_cache"]:
            return None
            
        cache_key = self._get_cache_key(artist, title)
        cache_entry = self.cache.get(cache_key)
        
        if cache_entry:
            # Check if cache entry is expired
            if cache_entry.get("expiration", 0) > time.time():
                logger.info(f"Cache hit for {artist} - {title}")
                return cache_entry["result"]
            else:
                # Remove expired entry
                del self.cache[cache_key]
                
        return None
    
    def search_videos(self, artist, title, max_results=None):
        """
        Search for videos matching the artist and title.
        
        Args:
            artist: Artist name
            title: Track title
            max_results: Maximum number of results to return
            
        Returns:
            List of video IDs
        """
        max_results = max_results or SEARCH_CONFIG["max_videos_to_check"]
        
        # Format search query
        query = SEARCH_CONFIG["query_format"].format(artist=artist, title=title)
        
        try:
            # Call the search.list method to retrieve results
            search_response = self.youtube.search().list(
                q=query,
                part="id",
                maxResults=max_results,
                type="video"
            ).execute()
            
            # Extract video IDs from search results
            video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
            
            # If no results, try alternative query format
            if not video_ids:
                alt_query = SEARCH_CONFIG["alt_query_format"].format(artist=artist, title=title)
                search_response = self.youtube.search().list(
                    q=alt_query,
                    part="id",
                    maxResults=max_results,
                    type="video"
                ).execute()
                video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
            
            return video_ids
        
        except HttpError as e:
            logger.error(f"YouTube API error during search: {str(e)}")
            return []
    
    def check_video_restrictions(self, video_id, region_code=None):
        """
        Check if a video has content restrictions.
        
        Args:
            video_id: YouTube video ID
            region_code: Region code to check restrictions for
            
        Returns:
            Dictionary with restriction information
        """
        region_code = region_code or YOUTUBE_API_CONFIG["default_region_code"]
        
        try:
            # Call the videos.list method to retrieve video details
            video_response = self.youtube.videos().list(
                id=video_id,
                part="contentDetails,status"
            ).execute()
            
            # Check if video exists
            if not video_response.get("items"):
                return {
                    "status": STATUS_CODES["UNKNOWN"],
                    "reason": "Video not found"
                }
            
            video = video_response["items"][0]
            restrictions = {}
            
            # Check for region restrictions
            content_details = video.get("contentDetails", {})
            if "regionRestriction" in content_details:
                region_restriction = content_details["regionRestriction"]
                
                # Check if video is blocked in the specified region
                if "blocked" in region_restriction and region_code in region_restriction["blocked"]:
                    return {
                        "status": STATUS_CODES["BLOCKED"],
                        "reason": "Blocked in region",
                        "details": region_restriction
                    }
                
                # Check if video is only allowed in specific regions
                if "allowed" in region_restriction and region_code not in region_restriction["allowed"]:
                    return {
                        "status": STATUS_CODES["BLOCKED"],
                        "reason": "Not allowed in region",
                        "details": region_restriction
                    }
                
                restrictions["regionRestriction"] = region_restriction
            
            # Check privacy status
            status = video.get("status", {})
            privacy_status = status.get("privacyStatus")
            
            if privacy_status and privacy_status != "public":
                return {
                    "status": STATUS_CODES["RESTRICTED"],
                    "reason": f"Privacy status: {privacy_status}",
                    "details": {"privacyStatus": privacy_status}
                }
            
            # If no restrictions found, video is available
            if not restrictions:
                return {
                    "status": STATUS_CODES["AVAILABLE"],
                    "reason": "No restrictions found"
                }
            else:
                # Video has some restrictions, but not blocked in the specified region
                return {
                    "status": STATUS_CODES["RESTRICTED"],
                    "reason": "Has restrictions in some regions",
                    "details": restrictions
                }
        
        except HttpError as e:
            logger.error(f"YouTube API error during restriction check: {str(e)}")
            return {
                "status": STATUS_CODES["UNKNOWN"],
                "reason": f"API error: {str(e)}"
            }
    
    def check_track_compatibility(self, artist, title, region_code=None):
        """
        Check if a track is compatible with YouTube.
        
        Args:
            artist: Artist name
            title: Track title
            region_code: Region code to check restrictions for
            
        Returns:
            Dictionary with compatibility information
        """
        # Check cache first
        cached_result = self._get_from_cache(artist, title)
        if cached_result:
            return cached_result
        
        # Search for videos matching the track
        video_ids = self.search_videos(artist, title)
        
        if not video_ids:
            result = {
                "track": {
                    "artist": artist,
                    "title": title
                },
                "status": STATUS_CODES["UNKNOWN"],
                "reason": "No videos found",
                "checked_videos": []
            }
            self._add_to_cache(artist, title, result)
            return result
        
        # Check restrictions for each video
        checked_videos = []
        blocked_count = 0
        
        for video_id in video_ids:
            restriction_info = self.check_video_restrictions(video_id, region_code)
            
            video_info = {
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "restrictions": restriction_info
            }
            
            checked_videos.append(video_info)
            
            if restriction_info["status"] == STATUS_CODES["BLOCKED"]:
                blocked_count += 1
        
        # Determine overall status based on checked videos
        if blocked_count == len(video_ids):
            status = STATUS_CODES["BLOCKED"]
            reason = "All videos are blocked"
        elif blocked_count > 0:
            status = STATUS_CODES["RESTRICTED"]
            reason = f"{blocked_count} out of {len(video_ids)} videos are blocked"
        elif len(checked_videos) > 0:
            status = STATUS_CODES["AVAILABLE"]
            reason = "No blocked videos found"
        else:
            status = STATUS_CODES["UNKNOWN"]
            reason = "No videos checked"
        
        result = {
            "track": {
                "artist": artist,
                "title": title
            },
            "status": status,
            "reason": reason,
            "checked_videos": checked_videos
        }
        
        # Cache the result
        self._add_to_cache(artist, title, result)
        
        return result
    
    def check_tracklist_compatibility(self, tracklist, region_code=None):
        """
        Check compatibility for a list of tracks.
        
        Args:
            tracklist: List of tracks with artist and title
            region_code: Region code to check restrictions for
            
        Returns:
            List of compatibility results
        """
        results = []
        
        for track in tracklist:
            artist = track.get("artist", "")
            title = track.get("title", "")
            
            if not artist or not title:
                logger.warning(f"Skipping track with missing artist or title: {track}")
                continue
            
            result = self.check_track_compatibility(artist, title, region_code)
            
            # Add original track info to result
            result["original_track"] = track
            
            results.append(result)
        
        # Save cache after processing all tracks
        self._save_cache()
        
        return results
    
    def close(self):
        """
        Close the YouTube API client and save cache.
        """
        self._save_cache()
        if hasattr(self, 'youtube') and self.youtube:
            self.youtube.close()
