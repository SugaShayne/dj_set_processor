"""
Core functionality for the Thumbnail Generator module.
"""

import os
import cv2
import numpy as np
import logging
import shutil
import random
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

from config import THUMBNAIL_CONFIG, LOGGING_CONFIG

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"],
    filename=LOGGING_CONFIG["file"]
)
logger = logging.getLogger('thumbnail_generator')

class ThumbnailGenerator:
    """
    Class for generating thumbnails from videos.
    """
    
    def __init__(self, config=None):
        """
        Initialize the ThumbnailGenerator.
        
        Args:
            config: Configuration for thumbnail generation
        """
        self.config = config or THUMBNAIL_CONFIG
        
        # Create temp directory if it doesn't exist
        os.makedirs(self.config["temp_dir"], exist_ok=True)
    
    def generate_thumbnails(self, video_path: str, output_dir: str, num_thumbnails: Optional[int] = None) -> List[str]:
        """
        Generate thumbnails from a video.
        
        Args:
            video_path: Path to the input video file
            output_dir: Directory to save the thumbnails
            num_thumbnails: Number of thumbnails to generate (optional)
            
        Returns:
            List of paths to the generated thumbnails
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Set number of thumbnails
        num_thumbnails = num_thumbnails or self.config["num_thumbnails"]
        
        logger.info(f"Generating {num_thumbnails} thumbnails from: {video_path}")
        
        # Extract frames from video
        frames = self._extract_frames(video_path, num_thumbnails)
        
        if not frames:
            raise ValueError("No suitable frames found in the video")
        
        logger.info(f"Extracted {len(frames)} frames")
        
        # Generate thumbnails from frames
        thumbnail_paths = []
        
        for i, (frame, timestamp) in enumerate(frames):
            # Convert OpenCV BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create PIL Image from numpy array
            image = Image.fromarray(frame_rgb)
            
            # Resize image to thumbnail size
            width, height = self.config["thumbnail_size"]
            image = image.resize((width, height), Image.LANCZOS)
            
            # Apply enhancements if enabled
            if self.config["enhance"]:
                image = self._enhance_image(image)
            
            # Add text overlay if enabled
            if self.config["add_text"]:
                image = self._add_text_overlay(image, f"Time: {self._format_timestamp(timestamp)}")
            
            # Save thumbnail
            file_name = f"thumbnail_{i+1:02d}.{self.config['format']}"
            output_path = os.path.join(output_dir, file_name)
            
            image.save(
                output_path,
                quality=self.config["quality"],
                optimize=True
            )
            
            thumbnail_paths.append(output_path)
            logger.info(f"Saved thumbnail {i+1}/{len(frames)}: {output_path}")
        
        return thumbnail_paths
    
    def _extract_frames(self, video_path: str, num_frames: int) -> List[Tuple[np.ndarray, float]]:
        """
        Extract frames from a video.
        
        Args:
            video_path: Path to the input video file
            num_frames: Number of frames to extract
            
        Returns:
            List of tuples containing (frame, timestamp)
        """
        # Open the video
        video = cv2.VideoCapture(video_path)
        
        if not video.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps > 0 else 0
        
        logger.info(f"Video properties: {frame_count} frames, {fps} fps, {duration:.2f} seconds")
        
        # Choose extraction method
        method = self.config["extraction_method"]
        
        if method == "uniform":
            frames = self._extract_uniform_frames(video, num_frames, frame_count, fps)
        elif method == "key_moments":
            frames = self._extract_key_moment_frames(video, num_frames, frame_count, fps)
        elif method == "random":
            frames = self._extract_random_frames(video, num_frames, frame_count, fps)
        else:
            logger.warning(f"Unknown extraction method: {method}, falling back to uniform")
            frames = self._extract_uniform_frames(video, num_frames, frame_count, fps)
        
        # Release the video
        video.release()
        
        return frames
    
    def _extract_uniform_frames(self, video: cv2.VideoCapture, num_frames: int, 
                               frame_count: int, fps: float) -> List[Tuple[np.ndarray, float]]:
        """
        Extract uniformly spaced frames from a video.
        
        Args:
            video: OpenCV VideoCapture object
            num_frames: Number of frames to extract
            frame_count: Total number of frames in the video
            fps: Frames per second
            
        Returns:
            List of tuples containing (frame, timestamp)
        """
        frames = []
        
        # Skip first and last 5% of the video
        start_frame = int(frame_count * 0.05)
        end_frame = int(frame_count * 0.95)
        usable_frame_count = end_frame - start_frame
        
        if usable_frame_count <= 0:
            # Video is too short, use all frames
            start_frame = 0
            end_frame = frame_count
            usable_frame_count = frame_count
        
        # Calculate frame indices to extract
        if num_frames >= usable_frame_count:
            # If we need more frames than available, use all frames
            frame_indices = list(range(start_frame, end_frame))
        else:
            # Calculate evenly spaced indices
            step = usable_frame_count / num_frames
            frame_indices = [int(start_frame + i * step) for i in range(num_frames)]
        
        # Extract frames
        for frame_idx in frame_indices:
            # Set position
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            
            # Read frame
            success, frame = video.read()
            
            if not success:
                logger.warning(f"Failed to read frame at index {frame_idx}")
                continue
            
            # Calculate timestamp
            timestamp = frame_idx / fps if fps > 0 else 0
            
            # Check frame quality
            if self._is_good_quality_frame(frame):
                frames.append((frame, timestamp))
        
        return frames
    
    def _extract_key_moment_frames(self, video: cv2.VideoCapture, num_frames: int, 
                                  frame_count: int, fps: float) -> List[Tuple[np.ndarray, float]]:
        """
        Extract frames at key moments (scene changes) from a video.
        
        Args:
            video: OpenCV VideoCapture object
            num_frames: Number of frames to extract
            frame_count: Total number of frames in the video
            fps: Frames per second
            
        Returns:
            List of tuples containing (frame, timestamp)
        """
        frames = []
        prev_frame = None
        frame_diffs = []
        
        # Skip first and last 5% of the video
        start_frame = int(frame_count * 0.05)
        end_frame = int(frame_count * 0.95)
        
        # Sample frames to calculate differences
        sample_rate = max(1, int(frame_count / 500))  # Sample at most 500 frames
        
        # Reset video position
        video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # Calculate frame differences
        for frame_idx in range(start_frame, end_frame, sample_rate):
            # Set position
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            
            # Read frame
            success, frame = video.read()
            
            if not success:
                continue
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # Calculate difference with previous frame
                diff = cv2.absdiff(gray, prev_frame)
                diff_score = np.sum(diff) / (diff.shape[0] * diff.shape[1])
                frame_diffs.append((frame_idx, diff_score, frame))
            
            prev_frame = gray
        
        # Sort by difference score (descending)
        frame_diffs.sort(key=lambda x: x[1], reverse=True)
        
        # Take top N frames with highest difference scores
        top_frames = frame_diffs[:min(num_frames * 2, len(frame_diffs))]
        
        # Sort by frame index
        top_frames.sort(key=lambda x: x[0])
        
        # Select evenly spaced frames from top frames
        if len(top_frames) > num_frames:
            step = len(top_frames) / num_frames
            selected_indices = [int(i * step) for i in range(num_frames)]
            top_frames = [top_frames[i] for i in selected_indices]
        
        # Extract frames
        for frame_idx, _, frame in top_frames:
            # Calculate timestamp
            timestamp = frame_idx / fps if fps > 0 else 0
            
            # Check frame quality
            if self._is_good_quality_frame(frame):
                frames.append((frame, timestamp))
        
        return frames
    
    def _extract_random_frames(self, video: cv2.VideoCapture, num_frames: int, 
                              frame_count: int, fps: float) -> List[Tuple[np.ndarray, float]]:
        """
        Extract random frames from a video.
        
        Args:
            video: OpenCV VideoCapture object
            num_frames: Number of frames to extract
            frame_count: Total number of frames in the video
            fps: Frames per second
            
        Returns:
            List of tuples containing (frame, timestamp)
        """
        frames = []
        
        # Skip first and last 5% of the video
        start_frame = int(frame_count * 0.05)
        end_frame = int(frame_count * 0.95)
        usable_frame_count = end_frame - start_frame
        
        if usable_frame_count <= 0:
            # Video is too short, use all frames
            start_frame = 0
            end_frame = frame_count
            usable_frame_count = frame_count
        
        # Generate random frame indices
        frame_indices = random.sample(
            range(start_frame, end_frame),
            min(num_frames * 3, usable_frame_count)  # Sample more frames than needed
        )
        
        # Extract frames
        for frame_idx in frame_indices:
            # Set position
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            
            # Read frame
            success, frame = video.read()
            
            if not success:
                logger.warning(f"Failed to read frame at index {frame_idx}")
                continue
            
            # Calculate timestamp
            timestamp = frame_idx / fps if fps > 0 else 0
            
            # Check frame quality
            if self._is_good_quality_frame(frame):
                frames.append((frame, timestamp))
                
                # Stop if we have enough frames
                if len(frames) >= num_frames:
                    break
        
        return frames
    
    def _is_good_quality_frame(self, frame: np.ndarray) -> bool:
        """
        Check if a frame is of good quality.
        
        Args:
            frame: OpenCV frame
            
        Returns:
            True if the frame is of good quality, False otherwise
        """
        # Check brightness
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        if brightness < self.config["min_brightness"]:
            return False
        
        # Check contrast
        contrast = np.std(gray)
        
        if contrast < self.config["min_contrast"]:
            return False
        
        # Check for blurriness
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = np.var(laplacian)
        
        if sharpness < 100:  # Arbitrary threshold for blurriness
            return False
        
        return True
    
    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """
        Enhance an image.
        
        Args:
            image: PIL Image
            
        Returns:
            Enhanced PIL Image
        """
        settings = self.config["enhancement_settings"]
        
        # Brightness
        if settings["brightness"] != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(settings["brightness"])
        
        # Contrast
        if settings["contrast"] != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(settings["contrast"])
        
        # Sharpness
        if settings["sharpness"] != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(settings["sharpness"])
        
        # Color saturation
        if settings["saturation"] != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(settings["saturation"])
        
        return image
    
    def _add_text_overlay(self, image: Image.Image, text: str) -> Image.Image:
        """
        Add text overlay to an image.
        
        Args:
            image: PIL Image
            text: Text to add
            
        Returns:
            PIL Image with text overlay
        """
        settings = self.config["text_settings"]
        draw = ImageDraw.Draw(image)
        
        # Try to load font, fall back to default if not available
        try:
            font = ImageFont.truetype(settings["font"], settings["font_size"])
        except IOError:
            font = ImageFont.load_default()
        
        # Calculate text size
        text_width, text_height = draw.textsize(text, font=font)
        
        # Calculate position
        width, height = image.size
        
        if settings["position"] == "top":
            position = ((width - text_width) // 2, 20)
        elif settings["position"] == "bottom":
            position = ((width - text_width) // 2, height - text_height - 20)
        else:  # center
            position = ((width - text_width) // 2, (height - text_height) // 2)
        
        # Draw text with stroke (outline)
        stroke_width = settings["stroke_width"]
        stroke_color = settings["stroke_color"]
        
        # Draw stroke
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx != 0 or dy != 0:
                    draw.text(
                        (position[0] + dx, position[1] + dy),
                        text,
                        font=font,
                        fill=stroke_color
                    )
        
        # Draw text
        draw.text(
            position,
            text,
            font=font,
            fill=settings["font_color"]
        )
        
        return image
    
    def _format_timestamp(self
(Content truncated due to size limit. Use line ranges to read in chunks)