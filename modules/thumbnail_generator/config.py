"""
Configuration for the Thumbnail Generator module.
"""

# Thumbnail generation configuration
THUMBNAIL_CONFIG = {
    # Number of thumbnails to generate
    "num_thumbnails": 10,
    
    # Thumbnail dimensions (width, height)
    "thumbnail_size": (1280, 720),
    
    # Output format
    "format": "jpg",
    
    # JPEG quality (1-100)
    "quality": 90,
    
    # Frame extraction method
    # "uniform" - evenly spaced frames
    # "key_moments" - frames at scene changes
    # "random" - random frames
    "extraction_method": "key_moments",
    
    # Minimum brightness threshold (0-255)
    # Frames below this brightness will be skipped
    "min_brightness": 30,
    
    # Minimum contrast threshold (0-100)
    # Frames below this contrast will be skipped
    "min_contrast": 20,
    
    # Whether to apply enhancements to thumbnails
    "enhance": True,
    
    # Enhancement settings
    "enhancement_settings": {
        "brightness": 1.1,    # Brightness factor (1.0 = original)
        "contrast": 1.2,      # Contrast factor (1.0 = original)
        "sharpness": 1.3,     # Sharpness factor (1.0 = original)
        "saturation": 1.2     # Color saturation factor (1.0 = original)
    },
    
    # Whether to add text overlay to thumbnails
    "add_text": False,
    
    # Text overlay settings
    "text_settings": {
        "font": "Arial",
        "font_size": 60,
        "font_color": (255, 255, 255),  # White
        "stroke_color": (0, 0, 0),      # Black
        "stroke_width": 2,
        "position": "bottom"  # "top", "bottom", "center"
    },
    
    # Temporary directory for processing
    "temp_dir": "/tmp/thumbnail_generator"
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": None  # Set to a file path to enable file logging
}
