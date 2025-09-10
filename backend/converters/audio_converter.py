import os
import io
import tempfile
from typing import BinaryIO
from pydub import AudioSegment
from pydub.utils import which

class AudioConverter:
    @staticmethod
    def convert_audio(input_file: BinaryIO, source_format: str, target_format: str) -> bytes:
        """Convert audio from one format to another"""
        try:
            input_file.seek(0)
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix=f'.{source_format.lower()}', delete=False) as temp_input:
                temp_input.write(input_file.read())
                temp_input_path = temp_input.name
            
            try:
                # Load audio file
                if source_format.lower() == 'mp3':
                    audio = AudioSegment.from_mp3(temp_input_path)
                elif source_format.lower() == 'wav':
                    audio = AudioSegment.from_wav(temp_input_path)
                elif source_format.lower() == 'ogg':
                    audio = AudioSegment.from_ogg(temp_input_path)
                elif source_format.lower() == 'flac':
                    audio = AudioSegment.from_file(temp_input_path, format='flac')
                elif source_format.lower() == 'm4a':
                    audio = AudioSegment.from_file(temp_input_path, format='m4a')
                elif source_format.lower() == 'aac':
                    audio = AudioSegment.from_file(temp_input_path, format='aac')
                elif source_format.lower() == 'wma':
                    audio = AudioSegment.from_file(temp_input_path, format='wma')
                elif source_format.lower() == 'aiff':
                    audio = AudioSegment.from_file(temp_input_path, format='aiff')
                elif source_format.lower() == 'au':
                    audio = AudioSegment.from_file(temp_input_path, format='au')
                else:
                    audio = AudioSegment.from_file(temp_input_path)
                
                # Export to target format
                output_buffer = io.BytesIO()
                
                # Set export parameters based on target format
                export_params = {}
                if target_format.lower() == 'mp3':
                    export_params = {
                        'format': 'mp3',
                        'bitrate': '320k',
                        'parameters': ['-q:a', '0']  # High quality
                    }
                elif target_format.lower() == 'wav':
                    export_params = {'format': 'wav'}
                elif target_format.lower() == 'flac':
                    export_params = {
                        'format': 'flac',
                        'parameters': ['-compression_level', '8']  # High compression
                    }
                elif target_format.lower() == 'ogg':
                    export_params = {
                        'format': 'ogg',
                        'parameters': ['-q:a', '6']  # Good quality
                    }
                elif target_format.lower() == 'aac':
                    export_params = {
                        'format': 'aac',
                        'bitrate': '256k'
                    }
                elif target_format.lower() == 'm4a':
                    export_params = {
                        'format': 'mp4',
                        'codec': 'aac',
                        'bitrate': '256k'
                    }
                elif target_format.lower() == 'wma':
                    export_params = {'format': 'wma'}
                elif target_format.lower() == 'aiff':
                    export_params = {'format': 'aiff'}
                elif target_format.lower() == 'au':
                    export_params = {'format': 'au'}
                else:
                    export_params = {'format': target_format.lower()}
                
                audio.export(output_buffer, **export_params)
                
                return output_buffer.getvalue()
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_input_path):
                    os.unlink(temp_input_path)
                    
        except Exception as e:
            raise Exception(f"Audio conversion failed: {str(e)}")
    
    @staticmethod
    def get_audio_info(input_file: BinaryIO, source_format: str) -> dict:
        """Get audio file information"""
        try:
            input_file.seek(0)
            
            with tempfile.NamedTemporaryFile(suffix=f'.{source_format.lower()}', delete=False) as temp_file:
                temp_file.write(input_file.read())
                temp_path = temp_file.name
            
            try:
                if source_format.lower() == 'mp3':
                    audio = AudioSegment.from_mp3(temp_path)
                elif source_format.lower() == 'wav':
                    audio = AudioSegment.from_wav(temp_path)
                else:
                    audio = AudioSegment.from_file(temp_path)
                
                return {
                    'duration_seconds': len(audio) / 1000.0,
                    'channels': audio.channels,
                    'frame_rate': audio.frame_rate,
                    'sample_width': audio.sample_width,
                    'max_possible_amplitude': audio.max_possible_amplitude
                }
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            return {'error': str(e)}