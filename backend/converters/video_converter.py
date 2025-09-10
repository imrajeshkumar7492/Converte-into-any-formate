import os
import io
import tempfile
from typing import BinaryIO
from moviepy.editor import VideoFileClip
import cv2
import numpy as np
from PIL import Image

class VideoConverter:
    @staticmethod
    def convert_video(input_file: BinaryIO, source_format: str, target_format: str) -> bytes:
        """Convert video from one format to another"""
        try:
            input_file.seek(0)
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix=f'.{source_format.lower()}', delete=False) as temp_input:
                temp_input.write(input_file.read())
                temp_input_path = temp_input.name
            
            with tempfile.NamedTemporaryFile(suffix=f'.{target_format.lower()}', delete=False) as temp_output:
                temp_output_path = temp_output.name
            
            try:
                # Load video
                video = VideoFileClip(temp_input_path)
                
                # Set codec based on target format
                codec_map = {
                    'mp4': 'libx264',
                    'avi': 'libx264',
                    'mov': 'libx264',
                    'wmv': 'libx264',
                    'flv': 'libx264',
                    'mkv': 'libx264',
                    'webm': 'libvpx',
                    'ogv': 'libtheora',
                    'm4v': 'libx264'
                }
                
                codec = codec_map.get(target_format.lower(), 'libx264')
                
                # Convert video
                if target_format.lower() == 'webm':
                    video.write_videofile(
                        temp_output_path,
                        codec=codec,
                        audio_codec='libvorbis',
                        temp_audiofile='temp-audio.m4a',
                        remove_temp=True
                    )
                elif target_format.lower() == 'ogv':
                    video.write_videofile(
                        temp_output_path,
                        codec=codec,
                        audio_codec='libvorbis',
                        temp_audiofile='temp-audio.ogg',
                        remove_temp=True
                    )
                else:
                    video.write_videofile(
                        temp_output_path,
                        codec=codec,
                        temp_audiofile='temp-audio.m4a',
                        remove_temp=True
                    )
                
                video.close()
                
                # Read converted file
                with open(temp_output_path, 'rb') as output_file:
                    return output_file.read()
                    
            finally:
                # Clean up temporary files
                for path in [temp_input_path, temp_output_path]:
                    if os.path.exists(path):
                        os.unlink(path)
                        
        except Exception as e:
            raise Exception(f"Video conversion failed: {str(e)}")
    
    @staticmethod
    def extract_audio_from_video(input_file: BinaryIO, source_format: str, target_audio_format: str) -> bytes:
        """Extract audio from video file"""
        try:
            input_file.seek(0)
            
            with tempfile.NamedTemporaryFile(suffix=f'.{source_format.lower()}', delete=False) as temp_input:
                temp_input.write(input_file.read())
                temp_input_path = temp_input.name
            
            with tempfile.NamedTemporaryFile(suffix=f'.{target_audio_format.lower()}', delete=False) as temp_output:
                temp_output_path = temp_output.name
            
            try:
                # Load video and extract audio
                video = VideoFileClip(temp_input_path)
                audio = video.audio
                
                if audio is None:
                    raise Exception("No audio track found in video")
                
                # Set codec based on target format
                if target_audio_format.lower() == 'mp3':
                    audio.write_audiofile(temp_output_path, codec='mp3')
                elif target_audio_format.lower() == 'wav':
                    audio.write_audiofile(temp_output_path, codec='pcm_s16le')
                elif target_audio_format.lower() == 'aac':
                    audio.write_audiofile(temp_output_path, codec='aac')
                elif target_audio_format.lower() == 'ogg':
                    audio.write_audiofile(temp_output_path, codec='libvorbis')
                else:
                    audio.write_audiofile(temp_output_path)
                
                audio.close()
                video.close()
                
                # Read extracted audio
                with open(temp_output_path, 'rb') as output_file:
                    return output_file.read()
                    
            finally:
                # Clean up temporary files
                for path in [temp_input_path, temp_output_path]:
                    if os.path.exists(path):
                        os.unlink(path)
                        
        except Exception as e:
            raise Exception(f"Audio extraction failed: {str(e)}")
    
    @staticmethod
    def convert_video_to_gif(input_file: BinaryIO, source_format: str, max_duration: int = 10) -> bytes:
        """Convert video to animated GIF"""
        try:
            input_file.seek(0)
            
            with tempfile.NamedTemporaryFile(suffix=f'.{source_format.lower()}', delete=False) as temp_input:
                temp_input.write(input_file.read())
                temp_input_path = temp_input.name
            
            try:
                # Load video
                video = VideoFileClip(temp_input_path)
                
                # Limit duration for GIF
                if video.duration > max_duration:
                    video = video.subclip(0, max_duration)
                
                # Resize if too large (GIFs should be smaller)
                if video.w > 640:
                    video = video.resize(width=640)
                
                # Convert to GIF
                output_buffer = io.BytesIO()
                
                # Extract frames and create GIF using PIL
                frames = []
                fps = min(video.fps, 10)  # Limit fps for smaller file size
                
                for t in np.arange(0, video.duration, 1.0/fps):
                    frame = video.get_frame(t)
                    pil_frame = Image.fromarray(frame)
                    frames.append(pil_frame)
                
                video.close()
                
                if frames:
                    frames[0].save(
                        output_buffer,
                        format='GIF',
                        save_all=True,
                        append_images=frames[1:],
                        duration=int(1000/fps),
                        loop=0,
                        optimize=True
                    )
                
                return output_buffer.getvalue()
                
            finally:
                if os.path.exists(temp_input_path):
                    os.unlink(temp_input_path)
                    
        except Exception as e:
            raise Exception(f"Video to GIF conversion failed: {str(e)}")
    
    @staticmethod
    def get_video_info(input_file: BinaryIO, source_format: str) -> dict:
        """Get video file information"""
        try:
            input_file.seek(0)
            
            with tempfile.NamedTemporaryFile(suffix=f'.{source_format.lower()}', delete=False) as temp_file:
                temp_file.write(input_file.read())
                temp_path = temp_file.name
            
            try:
                video = VideoFileClip(temp_path)
                
                info = {
                    'duration_seconds': video.duration,
                    'fps': video.fps,
                    'width': video.w,
                    'height': video.h,
                    'has_audio': video.audio is not None
                }
                
                video.close()
                return info
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            return {'error': str(e)}