"""
Multi-modal document loaders for images, audio, and other media types.
"""

import base64
import io
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from .loaders import BaseDocumentLoader, Document
from ..utils.exceptions import DocumentProcessingError
from ..utils.logging import LoggerMixin


class ImageLoader(BaseDocumentLoader, LoggerMixin):
    """Loader for image files with OCR and vision capabilities."""
    
    def __init__(self, extract_text: bool = True, extract_metadata: bool = True, **kwargs):
        """
        Initialize image loader.
        
        Args:
            extract_text: Whether to extract text using OCR
            extract_metadata: Whether to extract image metadata
        """
        super().__init__(**kwargs)
        self.extract_text = extract_text
        self.extract_metadata = extract_metadata
        self._ocr_engine = None
        self._vision_model = None
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Initialize OCR and vision processing engines."""
        if self.extract_text:
            try:
                import pytesseract
                self._ocr_engine = pytesseract
                self.logger.info("Initialized Tesseract OCR engine")
            except ImportError:
                self.logger.warning("pytesseract not available, OCR disabled")
        
        # Initialize vision model for image understanding
        try:
            # Placeholder for vision model initialization
            # In practice, you'd use models like CLIP, BLIP, etc.
            self._vision_model = "placeholder"
            self.logger.info("Vision model initialized")
        except Exception as e:
            self.logger.warning(f"Vision model initialization failed: {e}")
    
    async def load(self, file_path: Union[str, Path]) -> List[Document]:
        """Load and process image file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DocumentProcessingError(f"Image file not found: {file_path}")
        
        try:
            # Load image
            from PIL import Image
            image = Image.open(file_path)
            
            # Extract text using OCR
            extracted_text = ""
            if self.extract_text and self._ocr_engine:
                try:
                    extracted_text = self._ocr_engine.image_to_string(image)
                    self.logger.debug(f"Extracted {len(extracted_text)} characters via OCR")
                except Exception as e:
                    self.logger.warning(f"OCR extraction failed: {e}")
            
            # Generate image description using vision model
            description = ""
            if self._vision_model:
                description = await self._generate_image_description(image)
            
            # Combine text content
            content_parts = []
            if extracted_text.strip():
                content_parts.append(f"OCR Text: {extracted_text.strip()}")
            if description.strip():
                content_parts.append(f"Image Description: {description.strip()}")
            
            content = "\n\n".join(content_parts) if content_parts else f"Image file: {file_path.name}"
            
            # Extract metadata
            metadata = {
                "source": str(file_path),
                "type": "image",
                "format": image.format,
                "size": image.size,
                "mode": image.mode,
                "has_ocr_text": bool(extracted_text.strip()),
                "has_description": bool(description.strip())
            }
            
            if self.extract_metadata:
                # Extract EXIF data
                exif_data = getattr(image, '_getexif', lambda: None)()
                if exif_data:
                    metadata["exif"] = dict(exif_data)
            
            # Convert image to base64 for embedding
            img_buffer = io.BytesIO()
            image.save(img_buffer, format=image.format or 'PNG')
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            metadata["image_data"] = img_base64[:1000] + "..." if len(img_base64) > 1000 else img_base64
            
            document = Document(
                content=content,
                metadata=metadata,
                doc_type="image"
            )
            
            self.logger.info(f"Loaded image document: {file_path}")
            return [document]
            
        except ImportError:
            raise DocumentProcessingError("PIL (Pillow) not installed. Install with: pip install Pillow")
        except Exception as e:
            raise DocumentProcessingError(f"Failed to load image {file_path}: {e}")
    
    async def _generate_image_description(self, image) -> str:
        """Generate description of image content using vision model."""
        # Placeholder implementation
        # In practice, you'd use a vision-language model like BLIP, CLIP, etc.
        try:
            # Simulate image analysis
            width, height = image.size
            mode = image.mode
            
            # Basic description based on image properties
            description = f"Image with dimensions {width}x{height} in {mode} mode"
            
            # Add more sophisticated analysis here
            # e.g., object detection, scene understanding, etc.
            
            return description
        except Exception as e:
            self.logger.warning(f"Image description generation failed: {e}")
            return ""


class AudioLoader(BaseDocumentLoader, LoggerMixin):
    """Loader for audio files with speech-to-text capabilities."""
    
    def __init__(self, extract_transcript: bool = True, extract_metadata: bool = True, **kwargs):
        """
        Initialize audio loader.
        
        Args:
            extract_transcript: Whether to extract transcript using speech-to-text
            extract_metadata: Whether to extract audio metadata
        """
        super().__init__(**kwargs)
        self.extract_transcript = extract_transcript
        self.extract_metadata = extract_metadata
        self._speech_engine = None
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Initialize speech-to-text engine."""
        if self.extract_transcript:
            try:
                import speech_recognition as sr
                self._speech_engine = sr.Recognizer()
                self.logger.info("Initialized speech recognition engine")
            except ImportError:
                self.logger.warning("speech_recognition not available, transcript extraction disabled")
    
    async def load(self, file_path: Union[str, Path]) -> List[Document]:
        """Load and process audio file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DocumentProcessingError(f"Audio file not found: {file_path}")
        
        try:
            # Extract transcript
            transcript = ""
            if self.extract_transcript and self._speech_engine:
                transcript = await self._extract_transcript(file_path)
            
            # Extract audio metadata
            metadata = {
                "source": str(file_path),
                "type": "audio",
                "format": file_path.suffix.lower(),
                "has_transcript": bool(transcript.strip())
            }
            
            if self.extract_metadata:
                metadata.update(await self._extract_audio_metadata(file_path))
            
            # Create content
            content = transcript if transcript.strip() else f"Audio file: {file_path.name}"
            
            document = Document(
                content=content,
                metadata=metadata,
                doc_type="audio"
            )
            
            self.logger.info(f"Loaded audio document: {file_path}")
            return [document]
            
        except Exception as e:
            raise DocumentProcessingError(f"Failed to load audio {file_path}: {e}")
    
    async def _extract_transcript(self, file_path: Path) -> str:
        """Extract transcript from audio file."""
        try:
            import speech_recognition as sr
            
            # Convert audio to WAV if needed
            audio_file = self._convert_to_wav(file_path)
            
            # Extract transcript
            with sr.AudioFile(str(audio_file)) as source:
                audio_data = self._speech_engine.record(source)
                transcript = self._speech_engine.recognize_google(audio_data)
            
            self.logger.debug(f"Extracted transcript: {len(transcript)} characters")
            return transcript
            
        except Exception as e:
            self.logger.warning(f"Transcript extraction failed: {e}")
            return ""
    
    def _convert_to_wav(self, file_path: Path) -> Path:
        """Convert audio file to WAV format if needed."""
        if file_path.suffix.lower() == '.wav':
            return file_path
        
        try:
            from pydub import AudioSegment
            
            # Load audio file
            audio = AudioSegment.from_file(str(file_path))
            
            # Convert to WAV
            wav_path = file_path.with_suffix('.wav')
            audio.export(str(wav_path), format="wav")
            
            return wav_path
            
        except ImportError:
            raise DocumentProcessingError("pydub not installed. Install with: pip install pydub")
        except Exception as e:
            self.logger.warning(f"Audio conversion failed: {e}")
            return file_path
    
    async def _extract_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from audio file."""
        metadata = {}
        
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(str(file_path))
            
            metadata.update({
                "duration_seconds": len(audio) / 1000.0,
                "frame_rate": audio.frame_rate,
                "channels": audio.channels,
                "sample_width": audio.sample_width,
                "frame_count": audio.frame_count(),
                "max_possible_amplitude": audio.max_possible_amplitude
            })
            
        except Exception as e:
            self.logger.warning(f"Audio metadata extraction failed: {e}")
        
        return metadata


class VideoLoader(BaseDocumentLoader, LoggerMixin):
    """Loader for video files with frame extraction and analysis."""
    
    def __init__(self, extract_frames: bool = True, extract_audio: bool = True, **kwargs):
        """
        Initialize video loader.
        
        Args:
            extract_frames: Whether to extract and analyze key frames
            extract_audio: Whether to extract audio track
        """
        super().__init__(**kwargs)
        self.extract_frames = extract_frames
        self.extract_audio = extract_audio
        self.image_loader = ImageLoader() if extract_frames else None
        self.audio_loader = AudioLoader() if extract_audio else None
    
    async def load(self, file_path: Union[str, Path]) -> List[Document]:
        """Load and process video file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DocumentProcessingError(f"Video file not found: {file_path}")
        
        try:
            documents = []
            
            # Extract video metadata
            metadata = {
                "source": str(file_path),
                "type": "video",
                "format": file_path.suffix.lower()
            }
            
            # Extract key frames if requested
            if self.extract_frames and self.image_loader:
                frame_docs = await self._extract_key_frames(file_path)
                documents.extend(frame_docs)
            
            # Extract audio track if requested
            if self.extract_audio and self.audio_loader:
                audio_docs = await self._extract_audio_track(file_path)
                documents.extend(audio_docs)
            
            # Create main video document
            content = f"Video file: {file_path.name}"
            if documents:
                content += f" (Contains {len(documents)} extracted components)"
            
            main_doc = Document(
                content=content,
                metadata=metadata,
                doc_type="video"
            )
            documents.insert(0, main_doc)
            
            self.logger.info(f"Loaded video document with {len(documents)} components: {file_path}")
            return documents
            
        except Exception as e:
            raise DocumentProcessingError(f"Failed to load video {file_path}: {e}")
    
    async def _extract_key_frames(self, file_path: Path) -> List[Document]:
        """Extract key frames from video."""
        # Placeholder implementation
        # In practice, you'd use OpenCV or similar to extract frames
        self.logger.info(f"Key frame extraction not yet implemented for {file_path}")
        return []
    
    async def _extract_audio_track(self, file_path: Path) -> List[Document]:
        """Extract audio track from video."""
        try:
            # Extract audio using pydub/ffmpeg
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(str(file_path))
            audio_path = file_path.with_suffix('.wav')
            audio.export(str(audio_path), format="wav")
            
            # Process extracted audio
            audio_docs = await self.audio_loader.load(audio_path)
            
            # Clean up temporary file
            audio_path.unlink(missing_ok=True)
            
            return audio_docs
            
        except Exception as e:
            self.logger.warning(f"Audio track extraction failed: {e}")
            return []
