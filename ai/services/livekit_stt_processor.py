# ai/services/livekit_stt_processor.py

import asyncio
import logging
import numpy as np
from typing import Optional, Callable, Awaitable
from collections import deque
import time

from pipecat.frames.frames import AudioRawFrame, TranscriptionFrame
from pipecat.services.azure.stt import AzureSTTService
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

logger = logging.getLogger(__name__)

class LiveKitSTTProcessor:
    """
    Processes audio frames from LiveKit and converts them to transcriptions
    using Pipecat's STT services.
    """
    
    def __init__(self, stt_service: AzureSTTService):
        self.stt_service = stt_service
        self.audio_buffer = deque()
        self.buffer_duration_ms = 1000  # 1 second buffer
        self.sample_rate = 16000
        self.channels = 1
        self.bytes_per_sample = 2  # 16-bit audio
        self.is_processing = False
        self.last_transcription_time = 0
        self.min_transcription_interval = 0.5  # Minimum time between transcriptions
        
        # Callback for when transcription is received
        self.on_transcription: Optional[Callable[[str], Awaitable[None]]] = None
        
    def set_transcription_callback(self, callback: Callable[[str], Awaitable[None]]):
        """Set callback function to handle transcriptions"""
        self.on_transcription = callback
        
    async def process_audio_frame(self, audio_data: bytes, sample_rate: int, channels: int):
        """Process incoming audio frame from LiveKit"""
        try:
            # Convert to numpy array for processing
            if audio_data:
                # Add to buffer
                self.audio_buffer.append({
                    'data': audio_data,
                    'sample_rate': sample_rate,
                    'channels': channels,
                    'timestamp': time.time()
                })
                
                # Remove old audio data (keep only last buffer_duration_ms)
                current_time = time.time()
                while (self.audio_buffer and 
                       current_time - self.audio_buffer[0]['timestamp'] > self.buffer_duration_ms / 1000):
                    self.audio_buffer.popleft()
                
                # Process if we have enough audio and aren't already processing
                if (len(self.audio_buffer) >= 10 and  # At least 10 frames
                    not self.is_processing and
                    current_time - self.last_transcription_time > self.min_transcription_interval):
                    
                    asyncio.create_task(self._process_buffered_audio())
                    
        except Exception as e:
            logger.error(f"Error processing audio frame: {e}")
            
    async def _process_buffered_audio(self):
        """Process accumulated audio buffer through STT"""
        if self.is_processing:
            return
            
        self.is_processing = True
        
        try:
            # Concatenate buffered audio
            audio_chunks = []
            for frame in self.audio_buffer:
                audio_chunks.append(frame['data'])
            
            if not audio_chunks:
                return
                
            # Combine all audio data
            combined_audio = b''.join(audio_chunks)
            
            # Convert to numpy array
            audio_np = np.frombuffer(combined_audio, dtype=np.int16)
            
            # Check if we have enough audio (at least 0.5 seconds)
            min_samples = int(self.sample_rate * 0.5)
            if len(audio_np) < min_samples:
                return
            
            # Create Pipecat AudioRawFrame
            audio_frame = AudioRawFrame(
                audio=audio_np.tobytes(),
                sample_rate=self.sample_rate,
                num_channels=self.channels
            )
            
            # Process through STT service
            await self._process_through_stt(audio_frame)
            
            self.last_transcription_time = time.time()
            
        except Exception as e:
            logger.error(f"Error in STT processing: {e}")
        finally:
            self.is_processing = False
            
    async def _process_through_stt(self, Frame: AudioRawFrame):
        """Process audio frame through Pipecat STT service"""
        try:
            # Create a simple frame processor to handle STT output
            class STTFrameHandler(FrameProcessor):
                def __init__(self, parent):
                    super().__init__()
                    self.parent = parent
                    
                async def process_frame(self, frame, direction: FrameDirection):
                    if isinstance(frame, TranscriptionFrame):
                        if frame.text and frame.text.strip():
                            logger.info(f"STT transcription: {frame.text}")
                            if self.parent.on_transcription:
                                await self.parent.on_transcription(frame.text.strip())
                    
                    # Always push frame downstream
                    await self.push_frame(frame, direction)
            
            # Create handler
            handler = STTFrameHandler(self)
            
            # Connect STT service to handler
            self.stt_service = handler
            
            # Process the audio frame
            await self.stt_service.process_frame(audio_frame, FrameDirection.DOWNSTREAM) # type: ignore
            
        except Exception as e:
            logger.error(f"Error processing through STT service: {e}")
            
    def clear_buffer(self):
        """Clear the audio buffer"""
        self.audio_buffer.clear()
        
    def get_buffer_duration(self) -> float:
        """Get current buffer duration in seconds"""
        if not self.audio_buffer:
            return 0.0
        
        return time.time() - self.audio_buffer[0]['timestamp']