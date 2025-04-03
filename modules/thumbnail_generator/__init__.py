"""
Module initialization file for the Thumbnail Generator.
"""

from .thumbnail_generator import ThumbnailGenerator
from .config import THUMBNAIL_CONFIG, LOGGING_CONFIG

__all__ = [
    'ThumbnailGenerator',
    'THUMBNAIL_CONFIG',
    'LOGGING_CONFIG'
]
