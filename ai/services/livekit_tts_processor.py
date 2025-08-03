# ai/services/livekit_tts_processor.py

import asyncio
import logging
import numpy as np
from typing import Optional
from livekit import rtc

from pipecat.frames.frames import TextFrame, AudioRawFrame, TTSStartedFrame, TTSStoppedFrame
from pipecat.services.azure.tts import AzureTTSService
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

logger = logging.getLogger(__name__)

class LiveKitTTSProcessor:
    """
    Processes text through Pipecat TTS and streams audio to LiveKit.
    """
    
    def __init__(self, tts_service: AzureTTSService, audio_source: rtc.AudioSource):
        self.tts_service = tts_service
        self.audio_source = audio_source
        self.is_speaking = False
        
    async def speak_text(self, text: str):
        """Convert text to speech and stream to LiveKit"""
        if self.is_speaking:
            logger.info("Already speaking, skipping new text")
            return
            
        self.is_speaking = True
        
        try:
            logger.info(f"Converting to speech: {text[:100]}...")
            
            # Create a frame processor to handle TTS output
            class TTSFrameHandler(FrameProcessor):
                def __init__(self, parent):
                    super().__init__()
                    self.parent = parent
                    self.audio_chunks = []
                    
                async def process_frame(self, frame, direction: FrameDirection):
                    if isinstance(frame, TTSStartedFrame):
                        logger.info("TTS started")
                        self.audio_chunks = []
                        
                    elif isinstance(frame, AudioRawFrame):
                        # Collect audio chunks
                        self.audio_chunks.append(frame.audio)
                        
                    elif isinstance(frame, TTSStoppedFrame):
                        logger.info("TTS completed, streaming audio")
                        if self.audio_chunks:
                            await self.parent._stream_audio_chunks(self.audio_chunks)
                    
                    # Always push frame downstream
                    await self.push_frame(frame, direction)
            
            # Create handler
            handler = TTSFrameHandler(self)
            
            # Connect TTS service to handler
            self.tts_service = handler
            
            # Create text frame and process it
            text_frame = TextFrame(text=text)
            await self.tts_service.process_frame(text_frame, FrameDirection.DOWNSTREAM)
            
        except Exception as e:
            logger.error(f"Error in TTS processing: {e}")
        finally:
            self.is_speaking = False
            
    async def _stream_audio_chunks(self, audio_chunks):
        """Stream audio chunks to LiveKit"""
        try:
            # Combine all audio chunks
            combined_audio = b''.join(audio_chunks)
            
            if not combined_audio:
                logger.warning("No audio data to stream")
                return
                
            # Convert to numpy array
            audio_np = np.frombuffer(combined_audio, dtype=np.int16)
            
            # Stream in chunks to avoid overwhelming the audio source
            chunk_size = 1600  # 100ms at 16kHz
            sample_rate = 16000
            
            for i in range(0, len(audio_np), chunk_size):
                chunk = audio_np[i:i + chunk_size]
                
                if len(chunk) == 0:
                    continue
                    
                # Pad the last chunk if necessary
                if len(chunk) < chunk_size:
                    padded_chunk = np.zeros(chunk_size, dtype=np.int16)
                    padded_chunk[:len(chunk)] = chunk
                    chunk = padded_chunk
                
                # Create LiveKit audio frame
                frame = rtc.AudioFrame.create(sample_rate, 1, len(chunk))
                frame.data[:len(chunk) * 2] = chunk.tobytes()
                
                # Send to audio source
                await self.audio_source.capture_frame(frame)
                
                # Small delay to control playback rate
                await asyncio.sleep(0.1)  # 100ms delay between chunks
                
            logger.info(f"Successfully streamed {len(audio_np)} audio samples")
            
        except Exception as e:
            logger.error(f"Error streaming audio chunks: {e}")
            
    def is_currently_speaking(self) -> bool:
        """Check if TTS is currently active"""
        return self.is_speaking
        
    async def stop_speaking(self):
        """Stop current speech output"""
        # This would require more complex implementation to actually stop
        # ongoing TTS processing. For now, just reset the flag.
        self.is_speaking = False