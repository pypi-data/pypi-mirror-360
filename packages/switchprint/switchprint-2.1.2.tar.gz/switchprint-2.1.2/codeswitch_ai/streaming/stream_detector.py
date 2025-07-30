#!/usr/bin/env python3
"""Real-time streaming detection for live conversations."""

import time
import threading
import queue
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..detection.ensemble_detector import EnsembleDetector
from ..detection.fasttext_detector import FastTextDetector
from ..analysis.temporal_analysis import TemporalCodeSwitchAnalyzer
from .buffer_manager import SlidingWindowBuffer


@dataclass
class StreamChunk:
    """Represents a chunk of streaming text."""
    text: str
    timestamp: float
    chunk_id: int
    speaker_id: Optional[str] = None
    confidence_threshold: float = 0.5
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class StreamResult:
    """Result from streaming detection."""
    chunk: StreamChunk
    detected_languages: List[str]
    confidence: float
    switch_detected: bool
    processing_time_ms: float
    buffer_state: Dict[str, Any]
    temporal_patterns: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass 
class StreamingStatistics:
    """Statistics for streaming detection session."""
    total_chunks_processed: int
    total_switches_detected: int
    average_processing_time_ms: float
    languages_detected: set
    session_duration_seconds: float
    throughput_chunks_per_second: float
    buffer_efficiency: float
    temporal_pattern_counts: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['languages_detected'] = list(self.languages_detected)
        return result


@dataclass
class StreamingConfig:
    """Configuration for streaming detection."""
    # Buffer settings
    buffer_size: int = 50
    buffer_type: str = "sliding_window"  # circular, sliding_window, adaptive
    overlap_ratio: float = 0.3
    
    # Detection settings
    detector_type: str = "fasttext"  # fasttext, ensemble
    confidence_threshold: float = 0.6
    switch_sensitivity: float = 0.7
    
    # Performance settings
    max_workers: int = 2
    batch_size: int = 5
    enable_async: bool = True
    
    # Temporal analysis
    enable_temporal_analysis: bool = True
    temporal_window_size: int = 10
    
    # Real-time constraints
    max_latency_ms: float = 100.0
    queue_size: int = 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class StreamingDetector:
    """Real-time streaming detector for live conversations."""
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        """Initialize streaming detector.
        
        Args:
            config: Streaming configuration
        """
        self.config = config or StreamingConfig()
        
        # Initialize detector based on config
        if self.config.detector_type == "fasttext":
            self.detector = FastTextDetector()
        elif self.config.detector_type == "ensemble":
            self.detector = EnsembleDetector()
        else:
            raise ValueError(f"Unknown detector type: {self.config.detector_type}")
        
        # Initialize buffer
        self.buffer = SlidingWindowBuffer(
            max_size=self.config.buffer_size,
            overlap_ratio=self.config.overlap_ratio
        )
        
        # Initialize temporal analyzer if enabled
        self.temporal_analyzer = None
        if self.config.enable_temporal_analysis:
            self.temporal_analyzer = TemporalCodeSwitchAnalyzer()
        
        # Streaming state
        self.is_streaming = False
        self.chunk_counter = 0
        self.session_start_time = None
        self.statistics = None
        
        # Threading components
        self.input_queue = queue.Queue(maxsize=self.config.queue_size)
        self.output_queue = queue.Queue(maxsize=self.config.queue_size)
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        
        # Callbacks
        self.on_result_callback: Optional[Callable] = None
        self.on_switch_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        
        print(f"✓ Streaming detector initialized ({self.config.detector_type})")
    
    def set_callbacks(self, 
                     on_result: Optional[Callable] = None,
                     on_switch: Optional[Callable] = None,
                     on_error: Optional[Callable] = None) -> None:
        """Set callback functions for streaming events.
        
        Args:
            on_result: Called when detection result is ready
            on_switch: Called when language switch is detected
            on_error: Called when error occurs
        """
        self.on_result_callback = on_result
        self.on_switch_callback = on_switch
        self.on_error_callback = on_error
    
    def start_stream(self) -> None:
        """Start the streaming detection session."""
        if self.is_streaming:
            print("⚠ Streaming already active")
            return
        
        self.is_streaming = True
        self.session_start_time = time.time()
        self.chunk_counter = 0
        
        # Initialize statistics
        self.statistics = StreamingStatistics(
            total_chunks_processed=0,
            total_switches_detected=0,
            average_processing_time_ms=0.0,
            languages_detected=set(),
            session_duration_seconds=0.0,
            throughput_chunks_per_second=0.0,
            buffer_efficiency=0.0,
            temporal_pattern_counts=defaultdict(int)
        )
        
        # Start processing thread
        if self.config.enable_async:
            self._start_async_processing()
        else:
            self._start_sync_processing()
        
        print("🎥 Streaming detection started")
    
    def stop_stream(self) -> StreamingStatistics:
        """Stop the streaming detection session.
        
        Returns:
            Final session statistics
        """
        if not self.is_streaming:
            print("⚠ No active streaming session")
            return self.statistics
        
        self.is_streaming = False
        
        # Calculate final statistics
        if self.session_start_time:
            self.statistics.session_duration_seconds = time.time() - self.session_start_time
            if self.statistics.session_duration_seconds > 0:
                self.statistics.throughput_chunks_per_second = (
                    self.statistics.total_chunks_processed / self.statistics.session_duration_seconds
                )
        
        print(f"🛑 Streaming stopped. Processed {self.statistics.total_chunks_processed} chunks")
        return self.statistics
    
    def process_chunk(self, chunk: StreamChunk) -> StreamResult:
        """Process a single chunk synchronously.
        
        Args:
            chunk: Text chunk to process
            
        Returns:
            Detection result
        """
        start_time = time.time()
        
        try:
            # Add chunk to buffer
            self.buffer.add_chunk(chunk)
            
            # Get context from buffer
            context_text = self.buffer.get_context_text()
            
            # Perform detection
            detection_result = self.detector.detect_language(
                chunk.text,
                user_languages=chunk.context.get('user_languages') if chunk.context else None
            )
            
            # Check for language switch
            switch_detected = self._detect_switch(chunk, detection_result)
            
            # Temporal analysis if enabled
            temporal_patterns = None
            if self.temporal_analyzer and len(self.buffer.chunks) >= 3:
                temporal_patterns = self._analyze_temporal_patterns()
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Create result
            result = StreamResult(
                chunk=chunk,
                detected_languages=detection_result.detected_languages,
                confidence=detection_result.confidence,
                switch_detected=switch_detected,
                processing_time_ms=processing_time,
                buffer_state=self.buffer.get_state(),
                temporal_patterns=temporal_patterns
            )
            
            # Update statistics
            self._update_statistics(result)
            
            # Call callbacks
            if self.on_result_callback:
                self.on_result_callback(result)
            
            if switch_detected and self.on_switch_callback:
                self.on_switch_callback(result)
            
            return result
            
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(e)
            raise
    
    async def process_chunk_async(self, chunk: StreamChunk) -> StreamResult:
        """Process a chunk asynchronously.
        
        Args:
            chunk: Text chunk to process
            
        Returns:
            Detection result
        """
        loop = asyncio.get_event_loop()
        
        # Run detection in thread pool to avoid blocking
        result = await loop.run_in_executor(
            self.executor, 
            self.process_chunk, 
            chunk
        )
        
        return result
    
    def add_chunk(self, text: str, 
                  speaker_id: Optional[str] = None,
                  context: Optional[Dict[str, Any]] = None) -> None:
        """Add a text chunk to the processing queue.
        
        Args:
            text: Text content
            speaker_id: Optional speaker identifier
            context: Optional context information
        """
        if not self.is_streaming:
            print("⚠ Streaming not active. Call start_stream() first.")
            return
        
        chunk = StreamChunk(
            text=text,
            timestamp=time.time(),
            chunk_id=self.chunk_counter,
            speaker_id=speaker_id,
            confidence_threshold=self.config.confidence_threshold,
            context=context
        )
        
        self.chunk_counter += 1
        
        try:
            self.input_queue.put_nowait(chunk)
        except queue.Full:
            print("⚠ Input queue full, dropping chunk")
    
    def get_result(self, timeout: Optional[float] = None) -> Optional[StreamResult]:
        """Get the next available result.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Detection result or None if timeout
        """
        try:
            return self.output_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def _detect_switch(self, chunk: StreamChunk, detection_result) -> bool:
        """Detect if a language switch occurred.
        
        Args:
            chunk: Current chunk
            detection_result: Detection result
            
        Returns:
            True if switch detected
        """
        if len(self.buffer.chunks) < 2:
            return False
        
        # Get previous detection
        prev_chunks = self.buffer.get_recent_chunks(2)
        if len(prev_chunks) < 2:
            return False
        
        # Simple switch detection based on confidence and language change
        prev_result = self.detector.detect_language(prev_chunks[-2].text)
        
        current_lang = detection_result.detected_languages[0] if detection_result.detected_languages else 'unknown'
        prev_lang = prev_result.detected_languages[0] if prev_result.detected_languages else 'unknown'
        
        # Switch criteria
        confidence_high = detection_result.confidence >= self.config.switch_sensitivity
        language_changed = current_lang != prev_lang and current_lang != 'unknown' and prev_lang != 'unknown'
        
        return confidence_high and language_changed
    
    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in recent chunks.
        
        Returns:
            Temporal pattern analysis
        """
        if not self.temporal_analyzer:
            return {}
        
        # Get recent chunks for temporal analysis
        recent_chunks = self.buffer.get_recent_chunks(self.config.temporal_window_size)
        
        # Convert to messages format for temporal analyzer
        messages = [
            {
                'text': chunk.text,
                'timestamp': chunk.timestamp,
                'speaker_id': chunk.speaker_id or 'unknown'
            }
            for chunk in recent_chunks
        ]
        
        if len(messages) < 3:
            return {}
        
        try:
            # Analyze temporal patterns
            temporal_stats = self.temporal_analyzer.analyze_conversation_history(
                messages, session_id="streaming"
            )
            
            return {
                'pattern_trend': temporal_stats.pattern_trend,
                'switch_frequency': temporal_stats.switch_frequency,
                'dominant_pattern': temporal_stats.dominant_pattern.pattern_type if temporal_stats.dominant_pattern else None,
                'pattern_strength': temporal_stats.dominant_pattern.strength if temporal_stats.dominant_pattern else 0.0
            }
            
        except Exception as e:
            print(f"⚠ Temporal analysis failed: {e}")
            return {}
    
    def _update_statistics(self, result: StreamResult) -> None:
        """Update session statistics.
        
        Args:
            result: Processing result
        """
        self.statistics.total_chunks_processed += 1
        
        if result.switch_detected:
            self.statistics.total_switches_detected += 1
        
        # Update languages detected
        self.statistics.languages_detected.update(result.detected_languages)
        
        # Update average processing time
        total_time = (self.statistics.average_processing_time_ms * 
                     (self.statistics.total_chunks_processed - 1) + 
                     result.processing_time_ms)
        self.statistics.average_processing_time_ms = total_time / self.statistics.total_chunks_processed
        
        # Update temporal patterns
        if result.temporal_patterns and result.temporal_patterns.get('dominant_pattern'):
            pattern = result.temporal_patterns['dominant_pattern']
            self.statistics.temporal_pattern_counts[pattern] += 1
        
        # Update buffer efficiency
        if result.buffer_state:
            self.statistics.buffer_efficiency = result.buffer_state.get('efficiency', 0.0)
    
    def _start_async_processing(self) -> None:
        """Start asynchronous processing thread."""
        def async_worker():
            """Async worker thread."""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def process_loop():
                while self.is_streaming:
                    try:
                        # Get chunk from input queue
                        chunk = self.input_queue.get(timeout=0.1)
                        
                        # Process chunk asynchronously
                        result = await self.process_chunk_async(chunk)
                        
                        # Put result in output queue
                        self.output_queue.put_nowait(result)
                        
                    except queue.Empty:
                        continue
                    except Exception as e:
                        if self.on_error_callback:
                            self.on_error_callback(e)
                        print(f"⚠ Processing error: {e}")
            
            loop.run_until_complete(process_loop())
        
        thread = threading.Thread(target=async_worker, daemon=True)
        thread.start()
    
    def _start_sync_processing(self) -> None:
        """Start synchronous processing thread."""
        def sync_worker():
            """Sync worker thread."""
            while self.is_streaming:
                try:
                    # Get chunk from input queue
                    chunk = self.input_queue.get(timeout=0.1)
                    
                    # Process chunk
                    result = self.process_chunk(chunk)
                    
                    # Put result in output queue
                    self.output_queue.put_nowait(result)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    if self.on_error_callback:
                        self.on_error_callback(e)
                    print(f"⚠ Processing error: {e}")
        
        thread = threading.Thread(target=sync_worker, daemon=True)
        thread.start()
    
    def get_statistics(self) -> StreamingStatistics:
        """Get current session statistics.
        
        Returns:
            Current statistics
        """
        return self.statistics
    
    def reset_buffer(self) -> None:
        """Reset the internal buffer."""
        self.buffer.clear()
        print("🔄 Buffer reset")
    
    def get_buffer_state(self) -> Dict[str, Any]:
        """Get current buffer state.
        
        Returns:
            Buffer state information
        """
        return self.buffer.get_state()


def main():
    """Example usage of streaming detection."""
    print("🎥 Streaming Detection Example")
    print("=" * 40)
    
    # Initialize streaming detector
    config = StreamingConfig(
        detector_type="fasttext",
        buffer_size=20,
        confidence_threshold=0.6,
        enable_temporal_analysis=True
    )
    
    detector = StreamingDetector(config)
    
    # Set up callbacks
    def on_result(result: StreamResult):
        print(f"📊 Result: {result.detected_languages} (confidence: {result.confidence:.3f})")
        if result.switch_detected:
            print(f"🔄 Switch detected!")
    
    def on_switch(result: StreamResult):
        print(f"🚨 Language switch: {result.detected_languages}")
    
    def on_error(error: Exception):
        print(f"❌ Error: {error}")
    
    detector.set_callbacks(on_result=on_result, on_switch=on_switch, on_error=on_error)
    
    # Start streaming
    detector.start_stream()
    
    # Simulate streaming text chunks
    test_chunks = [
        "Hello everyone",
        "¿Cómo están todos?",
        "I hope you're doing well",
        "Estoy muy bien, gracias",
        "Let's continue with the meeting",
        "Sí, continuemos",
        "The next topic is important",
        "Es muy importante indeed"
    ]
    
    print("\n🔄 Processing streaming chunks:")
    
    for i, text in enumerate(test_chunks):
        print(f"\nChunk {i+1}: '{text}'")
        detector.add_chunk(text, speaker_id=f"speaker_{i % 2}")
        
        # Get result
        result = detector.get_result(timeout=2.0)
        if result:
            temporal_info = ""
            if result.temporal_patterns:
                pattern = result.temporal_patterns.get('dominant_pattern', 'none')
                temporal_info = f" | Pattern: {pattern}"
            
            print(f"  → {result.detected_languages} "
                  f"(conf: {result.confidence:.3f}, "
                  f"time: {result.processing_time_ms:.1f}ms{temporal_info})")
        
        # Small delay to simulate real-time
        time.sleep(0.1)
    
    # Stop streaming and get statistics
    stats = detector.stop_stream()
    
    print("\n📈 Session Statistics:")
    print(f"  Chunks processed: {stats.total_chunks_processed}")
    print(f"  Switches detected: {stats.total_switches_detected}")
    print(f"  Average processing time: {stats.average_processing_time_ms:.2f}ms")
    print(f"  Languages detected: {list(stats.languages_detected)}")
    print(f"  Throughput: {stats.throughput_chunks_per_second:.2f} chunks/sec")
    
    print("\n✓ Streaming detection example completed")


if __name__ == "__main__":
    main()