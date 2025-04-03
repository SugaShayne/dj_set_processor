"""
Core functionality for the Tracklist Generator module.
"""

import os
import json
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
from pydub import AudioSegment
import numpy as np
from datetime import datetime

from config import DATABASE_CONFIG, FINGERPRINTING_CONFIG, SUPPORTED_FORMATS, CONFIDENCE_THRESHOLD

class TracklistGenerator:
    """
    Class for generating tracklists from DJ sets using audio fingerprinting.
    """
    
    def __init__(self, config=None, db_config=None):
        """
        Initialize the TracklistGenerator.
        
        Args:
            config: Configuration for audio fingerprinting
            db_config: Database configuration
        """
        self.config = config or FINGERPRINTING_CONFIG
        self.db_config = db_config or DATABASE_CONFIG
        self.djv = Dejavu(self.db_config)
        
    def fingerprint_reference_tracks(self, directory_path, extensions=None):
        """
        Fingerprint reference tracks from a directory.
        
        Args:
            directory_path: Path to directory containing reference tracks
            extensions: List of file extensions to include
            
        Returns:
            Number of tracks fingerprinted
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
            
        extensions = extensions or SUPPORTED_FORMATS
        
        # Fingerprint all files in the directory with the specified extensions
        return self.djv.fingerprint_directory(directory_path, extensions, 
                                             self.config.get("processes", 4))
    
    def fingerprint_single_track(self, file_path):
        """
        Fingerprint a single reference track.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Song ID if successful, None otherwise
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Extract file name without extension
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Fingerprint the file
        return self.djv.fingerprint_file(file_path, song_name=file_name)
    
    def identify_tracks_in_mix(self, mix_file_path):
        """
        Identify tracks in a DJ mix using audio fingerprinting.
        
        Args:
            mix_file_path: Path to the DJ mix audio file
            
        Returns:
            List of identified tracks with timestamps
        """
        if not os.path.exists(mix_file_path):
            raise FileNotFoundError(f"File not found: {mix_file_path}")
        
        # Recognize the file
        results = self.djv.recognize(FileRecognizer, mix_file_path)
        
        # Process results
        if results["matches"]:
            # Sort matches by confidence
            matches = sorted(results["matches"], key=lambda x: x["offset_seconds"])
            
            # Filter matches by confidence threshold
            filtered_matches = [match for match in matches 
                               if match["fingerprinted_confidence"] > CONFIDENCE_THRESHOLD]
            
            # Group matches that are close together (likely the same track)
            grouped_matches = self._group_matches(filtered_matches)
            
            # Format the results
            tracklist = []
            for i, group in enumerate(grouped_matches):
                # Use the match with highest confidence in each group
                best_match = max(group, key=lambda x: x["fingerprinted_confidence"])
                
                # Calculate approximate end time
                end_time = None
                if i < len(grouped_matches) - 1:
                    end_time = grouped_matches[i+1][0]["offset_seconds"]
                
                track_info = {
                    "id": i + 1,
                    "track_name": best_match["song_name"],
                    "confidence": best_match["fingerprinted_confidence"],
                    "start_time": best_match["offset_seconds"],
                    "end_time": end_time,
                    "start_time_formatted": self._format_time(best_match["offset_seconds"]),
                    "end_time_formatted": self._format_time(end_time) if end_time else None
                }
                tracklist.append(track_info)
            
            return tracklist
        else:
            return []
    
    def _group_matches(self, matches, time_threshold=30):
        """
        Group matches that are close together in time.
        
        Args:
            matches: List of matches
            time_threshold: Time threshold in seconds
            
        Returns:
            List of grouped matches
        """
        if not matches:
            return []
            
        # Sort matches by offset time
        sorted_matches = sorted(matches, key=lambda x: x["offset_seconds"])
        
        # Group matches
        groups = []
        current_group = [sorted_matches[0]]
        
        for i in range(1, len(sorted_matches)):
            current_match = sorted_matches[i]
            previous_match = sorted_matches[i-1]
            
            # If the current match is close to the previous one, add it to the current group
            if current_match["offset_seconds"] - previous_match["offset_seconds"] < time_threshold:
                current_group.append(current_match)
            else:
                # Otherwise, start a new group
                groups.append(current_group)
                current_group = [current_match]
        
        # Add the last group
        if current_group:
            groups.append(current_group)
            
        return groups
    
    def _format_time(self, seconds):
        """
        Format time in seconds to HH:MM:SS format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        if seconds is None:
            return None
            
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def extract_audio_from_video(self, video_path, output_path=None):
        """
        Extract audio from a video file.
        
        Args:
            video_path: Path to the video file
            output_path: Path to save the extracted audio
            
        Returns:
            Path to the extracted audio file
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"File not found: {video_path}")
            
        # Generate output path if not provided
        if output_path is None:
            file_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(os.path.dirname(video_path), f"{file_name}.wav")
        
        # Extract audio using pydub
        video = AudioSegment.from_file(video_path)
        video.export(output_path, format="wav")
        
        return output_path
    
    def generate_tracklist_from_video(self, video_path):
        """
        Generate a tracklist from a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of identified tracks with timestamps
        """
        # Extract audio from video
        audio_path = self.extract_audio_from_video(video_path)
        
        # Identify tracks in the audio
        tracklist = self.identify_tracks_in_mix(audio_path)
        
        # Add metadata
        result = {
            "video_file": os.path.basename(video_path),
            "processed_date": datetime.now().isoformat(),
            "track_count": len(tracklist),
            "tracks": tracklist
        }
        
        return result
    
    def save_tracklist_to_json(self, tracklist, output_path):
        """
        Save tracklist to a JSON file.
        
        Args:
            tracklist: Tracklist data
            output_path: Path to save the JSON file
            
        Returns:
            Path to the saved file
        """
        with open(output_path, 'w') as f:
            json.dump(tracklist, f, indent=4)
        
        return output_path
