"""
Core functionality for the Video Editor module.
"""

import os
import json
import logging
import shutil
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union

from moviepy.editor import (
    VideoFileClip, 
    concatenate_videoclips, 
    CompositeVideoClip,
    clips_array
)

from config import VIDEO_EDITING_CONFIG, LOGGING_CONFIG

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"],
    filename=LOGGING_CONFIG["file"]
)
logger = logging.getLogger('video_editor')

class VideoEditor:
    """
    Class for editing videos to remove blocked segments and add transitions.
    """
    
    def __init__(self, config=None):
        """
        Initialize the VideoEditor.
        
        Args:
            config: Configuration for video editing
        """
        self.config = config or VIDEO_EDITING_CONFIG
        
        # Create temp directory if it doesn't exist
        os.makedirs(self.config["temp_dir"], exist_ok=True)
    
    def edit_video(self, video_path: str, segments_to_remove: List[Dict], output_path: Optional[str] = None) -> str:
        """
        Edit a video to remove specified segments and add transitions.
        
        Args:
            video_path: Path to the input video file
            segments_to_remove: List of segments to remove, each with start_time and end_time in seconds
            output_path: Path to save the output video (optional)
            
        Returns:
            Path to the edited video
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Generate output path if not provided
        if output_path is None:
            file_name, ext = os.path.splitext(os.path.basename(video_path))
            output_path = os.path.join(
                os.path.dirname(video_path),
                f"{file_name}_edited.{self.config['format']}"
            )
        
        logger.info(f"Editing video: {video_path}")
        logger.info(f"Removing {len(segments_to_remove)} segments")
        
        # Load the video
        video = VideoFileClip(video_path)
        
        # Sort segments by start time
        segments_to_remove = sorted(segments_to_remove, key=lambda x: x["start_time"])
        
        # Validate segments
        self._validate_segments(segments_to_remove, video.duration)
        
        # Get segments to keep (inverse of segments to remove)
        segments_to_keep = self._get_segments_to_keep(segments_to_remove, video.duration)
        
        # Merge short segments if needed
        if self.config["min_segment_duration"] > 0:
            segments_to_keep = self._merge_short_segments(segments_to_keep)
        
        logger.info(f"Keeping {len(segments_to_keep)} segments")
        
        # Extract the segments to keep
        clips = []
        for i, segment in enumerate(segments_to_keep):
            start_time = segment["start_time"]
            end_time = segment["end_time"]
            
            # Skip segments with zero or negative duration
            if end_time <= start_time:
                continue
                
            logger.info(f"Extracting segment {i+1}: {start_time:.2f}s - {end_time:.2f}s")
            clip = video.subclip(start_time, end_time)
            clips.append(clip)
        
        # If no clips remain, return error
        if not clips:
            video.close()
            raise ValueError("No segments remain after editing")
        
        # Concatenate the clips with transitions
        transition_type = self.config["transition_type"]
        transition_duration = self.config["transition_duration"]
        
        logger.info(f"Concatenating {len(clips)} clips with {transition_type} transitions")
        
        if transition_type == "crossfade" and len(clips) > 1:
            final_clip = concatenate_videoclips(
                clips, 
                method="crossfade",
                crossfade_duration=transition_duration
            )
        elif transition_type == "fade" and len(clips) > 1:
            # Apply fade out to all clips except the last one
            for i in range(len(clips) - 1):
                clips[i] = clips[i].fadeout(transition_duration)
            
            # Apply fade in to all clips except the first one
            for i in range(1, len(clips)):
                clips[i] = clips[i].fadein(transition_duration)
            
            final_clip = concatenate_videoclips(clips)
        else:
            # No transition or only one clip
            final_clip = concatenate_videoclips(clips)
        
        # Set resolution if specified
        if self.config["resolution"]:
            width, height = self.config["resolution"]
            final_clip = final_clip.resize((width, height))
        
        # Write the output file
        logger.info(f"Writing output to: {output_path}")
        
        final_clip.write_videofile(
            output_path,
            codec=self.config["codec"],
            bitrate=self.config["bitrate"],
            audio_codec=self.config["audio_codec"],
            audio_bitrate=self.config["audio_bitrate"],
            threads=self.config["threads"],
            verbose=False,
            logger=None if self.config["show_progress"] else "bar"
        )
        
        # Close all clips
        for clip in clips:
            clip.close()
        final_clip.close()
        video.close()
        
        logger.info("Video editing completed successfully")
        
        return output_path
    
    def edit_video_from_tracklist(self, video_path: str, tracklist_path: str, output_path: Optional[str] = None) -> str:
        """
        Edit a video based on a tracklist with compatibility information.
        
        Args:
            video_path: Path to the input video file
            tracklist_path: Path to the tracklist JSON file with compatibility info
            output_path: Path to save the output video (optional)
            
        Returns:
            Path to the edited video
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        if not os.path.exists(tracklist_path):
            raise FileNotFoundError(f"Tracklist file not found: {tracklist_path}")
        
        # Load tracklist
        with open(tracklist_path, 'r') as f:
            tracklist_data = json.load(f)
        
        # Extract tracks from tracklist
        if 'tracks' in tracklist_data:
            tracks = tracklist_data['tracks']
        else:
            tracks = tracklist_data
        
        # Find blocked tracks
        segments_to_remove = []
        
        for track in tracks:
            # Check if track is blocked
            is_blocked = False
            
            # Check if track has compatibility info
            if 'status' in track:
                is_blocked = track['status'] == 'blocked'
            elif 'compatibility' in track:
                is_blocked = track['compatibility'].get('status') == 'blocked'
            
            # If track is blocked and has start/end times, add to segments to remove
            if is_blocked:
                start_time = track.get('start_time')
                end_time = track.get('end_time')
                
                if start_time is not None and end_time is not None:
                    segments_to_remove.append({
                        'start_time': float(start_time),
                        'end_time': float(end_time)
                    })
        
        logger.info(f"Found {len(segments_to_remove)} blocked segments in tracklist")
        
        # Edit the video
        return self.edit_video(video_path, segments_to_remove, output_path)
    
    def _validate_segments(self, segments: List[Dict], video_duration: float) -> None:
        """
        Validate segments to ensure they are within video bounds.
        
        Args:
            segments: List of segments with start_time and end_time
            video_duration: Duration of the video in seconds
        """
        for i, segment in enumerate(segments):
            # Ensure segment has required fields
            if 'start_time' not in segment or 'end_time' not in segment:
                raise ValueError(f"Segment {i} missing start_time or end_time")
            
            # Convert to float if necessary
            segment['start_time'] = float(segment['start_time'])
            segment['end_time'] = float(segment['end_time'])
            
            # Ensure segment is within video bounds
            if segment['start_time'] < 0:
                logger.warning(f"Segment {i} start time ({segment['start_time']}) < 0, clamping to 0")
                segment['start_time'] = 0
                
            if segment['end_time'] > video_duration:
                logger.warning(f"Segment {i} end time ({segment['end_time']}) > video duration ({video_duration}), clamping to video duration")
                segment['end_time'] = video_duration
                
            # Ensure segment has positive duration
            if segment['end_time'] <= segment['start_time']:
                logger.warning(f"Segment {i} has zero or negative duration, skipping")
    
    def _get_segments_to_keep(self, segments_to_remove: List[Dict], video_duration: float) -> List[Dict]:
        """
        Get segments to keep based on segments to remove.
        
        Args:
            segments_to_remove: List of segments to remove
            video_duration: Duration of the video in seconds
            
        Returns:
            List of segments to keep
        """
        segments_to_keep = []
        
        # If no segments to remove, keep the entire video
        if not segments_to_remove:
            return [{'start_time': 0, 'end_time': video_duration}]
        
        # Add segment from start to first segment to remove
        if segments_to_remove[0]['start_time'] > 0:
            segments_to_keep.append({
                'start_time': 0,
                'end_time': segments_to_remove[0]['start_time']
            })
        
        # Add segments between segments to remove
        for i in range(len(segments_to_remove) - 1):
            current_end = segments_to_remove[i]['end_time']
            next_start = segments_to_remove[i + 1]['start_time']
            
            if next_start > current_end:
                segments_to_keep.append({
                    'start_time': current_end,
                    'end_time': next_start
                })
        
        # Add segment from last segment to remove to end
        if segments_to_remove[-1]['end_time'] < video_duration:
            segments_to_keep.append({
                'start_time': segments_to_remove[-1]['end_time'],
                'end_time': video_duration
            })
        
        return segments_to_keep
    
    def _merge_short_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Merge segments that are shorter than the minimum duration.
        
        Args:
            segments: List of segments with start_time and end_time
            
        Returns:
            List of merged segments
        """
        if not segments:
            return []
            
        min_duration = self.config["min_segment_duration"]
        
        # If only one segment, return it
        if len(segments) == 1:
            return segments
        
        merged_segments = [segments[0]]
        
        for segment in segments[1:]:
            last_segment = merged_segments[-1]
            
            # Check if current segment is too short
            if segment['end_time'] - segment['start_time'] < min_duration:
                # If last segment is also short, merge them
                if last_segment['end_time'] - last_segment['start_time'] < min_duration:
                    merged_segments[-1] = {
                        'start_time': last_segment['start_time'],
                        'end_time': segment['end_time']
                    }
                else:
                    # Otherwise, add it anyway
                    merged_segments.append(segment)
            else:
                # Segment is long enough, add it
                merged_segments.append(segment)
        
        return merged_segments
    
    def extract_frame(self, video_path: str, time: float, output_path: Optional[str] = None) -> str:
        """
        Extract a frame from a video at a specific time.
        
        Args:
            video_path: Path to the input video file
            time: Time in seconds to extract frame
            output_path: Path to save the output image (optional)
            
        Returns:
            Path to the extracted frame
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Generate output path if not provided
        if output_path is None:
            file_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(
                os.path.dirname(video_path),
                f"{file_name}_frame_{int(time)}.jpg"
            )
        
        # Load the video
        video = VideoFileClip(video_path)
        
        # Ensure time is within video bounds
        if time < 0:
            time = 0
        if time > video.duration:
            time = video.duration
        
        # Extract the frame
        video.save_frame(output_path, t=time)
        
        # Close the video
        video.close()
        
        return output_path
    
    def cleanup(self):
        """
        Clean up temporary files.
        """
        if os.path.exists(self.config["temp_dir"]):
            shutil.rmtree(self.config["temp_dir"])
            logger.info(f"Cleaned up temporary directory: {self.config['temp_dir']}")
