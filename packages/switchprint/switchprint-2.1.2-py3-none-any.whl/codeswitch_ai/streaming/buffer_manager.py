#!/usr/bin/env python3
"""Buffer management for streaming detection."""

import time
from typing import Dict, List, Optional, Any
from collections import deque
from dataclasses import dataclass
import numpy as np


@dataclass
class BufferChunk:
    """Chunk stored in buffer."""
    text: str
    timestamp: float
    chunk_id: int
    speaker_id: Optional[str] = None
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'text': self.text,
            'timestamp': self.timestamp,
            'chunk_id': self.chunk_id,
            'speaker_id': self.speaker_id,
            'processed': self.processed
        }


class CircularBuffer:
    """Circular buffer for fixed-size streaming data."""
    
    def __init__(self, max_size: int = 50):
        """Initialize circular buffer.
        
        Args:
            max_size: Maximum number of chunks to store
        """
        self.max_size = max_size
        self.chunks = deque(maxlen=max_size)
        self.total_added = 0
    
    def add_chunk(self, chunk) -> None:
        """Add a chunk to the buffer.
        
        Args:
            chunk: StreamChunk to add
        """
        buffer_chunk = BufferChunk(
            text=chunk.text,
            timestamp=chunk.timestamp,
            chunk_id=chunk.chunk_id,
            speaker_id=chunk.speaker_id
        )
        
        self.chunks.append(buffer_chunk)
        self.total_added += 1
    
    def get_recent_chunks(self, n: int) -> List[BufferChunk]:
        """Get the n most recent chunks.
        
        Args:
            n: Number of recent chunks to return
            
        Returns:
            List of recent chunks
        """
        return list(self.chunks)[-n:] if n <= len(self.chunks) else list(self.chunks)
    
    def get_context_text(self, n: int = 5) -> str:
        """Get context text from recent chunks.
        
        Args:
            n: Number of chunks for context
            
        Returns:
            Combined context text
        """
        recent_chunks = self.get_recent_chunks(n)
        return ' '.join(chunk.text for chunk in recent_chunks)
    
    def clear(self) -> None:
        """Clear the buffer."""
        self.chunks.clear()
    
    def get_state(self) -> Dict[str, Any]:
        """Get buffer state information.
        
        Returns:
            Buffer state dictionary
        """
        return {
            'size': len(self.chunks),
            'max_size': self.max_size,
            'total_added': self.total_added,
            'utilization': len(self.chunks) / self.max_size,
            'efficiency': min(len(self.chunks) / max(self.max_size * 0.8, 1), 1.0)
        }


class SlidingWindowBuffer:
    """Sliding window buffer with overlap for streaming detection."""
    
    def __init__(self, max_size: int = 50, overlap_ratio: float = 0.3):
        """Initialize sliding window buffer.
        
        Args:
            max_size: Maximum number of chunks to store
            overlap_ratio: Ratio of overlap between windows (0.0 to 1.0)
        """
        self.max_size = max_size
        self.overlap_ratio = max(0.0, min(1.0, overlap_ratio))
        self.chunks = deque(maxlen=max_size)
        self.window_id = 0
        self.total_added = 0
        
        # Calculate window parameters
        self.window_size = max_size
        self.step_size = int(max_size * (1 - overlap_ratio))
        self.overlap_size = max_size - self.step_size
    
    def add_chunk(self, chunk) -> None:
        """Add a chunk to the sliding window.
        
        Args:
            chunk: StreamChunk to add
        """
        buffer_chunk = BufferChunk(
            text=chunk.text,
            timestamp=chunk.timestamp,
            chunk_id=chunk.chunk_id,
            speaker_id=chunk.speaker_id
        )
        
        self.chunks.append(buffer_chunk)
        self.total_added += 1
        
        # Check if we need to slide the window
        if len(self.chunks) >= self.max_size:
            self._slide_window()
    
    def _slide_window(self) -> None:
        """Slide the window by removing old chunks."""
        # Remove chunks beyond the step size to maintain overlap
        chunks_to_remove = len(self.chunks) - self.overlap_size
        
        for _ in range(max(0, chunks_to_remove)):
            if self.chunks:
                self.chunks.popleft()
        
        self.window_id += 1
    
    def get_recent_chunks(self, n: int) -> List[BufferChunk]:
        """Get the n most recent chunks.
        
        Args:
            n: Number of recent chunks to return
            
        Returns:
            List of recent chunks
        """
        return list(self.chunks)[-n:] if n <= len(self.chunks) else list(self.chunks)
    
    def get_window_chunks(self) -> List[BufferChunk]:
        """Get all chunks in the current window.
        
        Returns:
            All chunks in current window
        """
        return list(self.chunks)
    
    def get_context_text(self, n: Optional[int] = None) -> str:
        """Get context text from recent chunks.
        
        Args:
            n: Number of chunks for context (None for all)
            
        Returns:
            Combined context text
        """
        if n is None:
            chunks = list(self.chunks)
        else:
            chunks = self.get_recent_chunks(n)
        
        return ' '.join(chunk.text for chunk in chunks)
    
    def clear(self) -> None:
        """Clear the buffer."""
        self.chunks.clear()
        self.window_id = 0
    
    def get_state(self) -> Dict[str, Any]:
        """Get buffer state information.
        
        Returns:
            Buffer state dictionary
        """
        return {
            'size': len(self.chunks),
            'max_size': self.max_size,
            'window_id': self.window_id,
            'overlap_ratio': self.overlap_ratio,
            'step_size': self.step_size,
            'overlap_size': self.overlap_size,
            'total_added': self.total_added,
            'utilization': len(self.chunks) / self.max_size,
            'efficiency': min(len(self.chunks) / max(self.max_size * 0.7, 1), 1.0)
        }


class AdaptiveBuffer:
    """Adaptive buffer that adjusts size based on content characteristics."""
    
    def __init__(self, 
                 initial_size: int = 30,
                 min_size: int = 10,
                 max_size: int = 100,
                 adaptation_rate: float = 0.1):
        """Initialize adaptive buffer.
        
        Args:
            initial_size: Initial buffer size
            min_size: Minimum buffer size
            max_size: Maximum buffer size
            adaptation_rate: Rate of size adaptation (0.0 to 1.0)
        """
        self.current_size = initial_size
        self.min_size = min_size
        self.max_size = max_size
        self.adaptation_rate = max(0.0, min(1.0, adaptation_rate))
        
        self.chunks = deque(maxlen=self.current_size)
        self.total_added = 0
        
        # Adaptation metrics
        self.recent_switch_rate = 0.0
        self.recent_complexity_score = 0.0
        self.adaptation_history = deque(maxlen=20)
    
    def add_chunk(self, chunk) -> None:
        """Add a chunk and adapt buffer size if needed.
        
        Args:
            chunk: StreamChunk to add
        """
        buffer_chunk = BufferChunk(
            text=chunk.text,
            timestamp=chunk.timestamp,
            chunk_id=chunk.chunk_id,
            speaker_id=chunk.speaker_id
        )
        
        # Analyze chunk characteristics
        complexity = self._analyze_chunk_complexity(buffer_chunk)
        
        # Update buffer if size changed
        if len(self.chunks) != self.current_size:
            new_chunks = deque(self.chunks, maxlen=self.current_size)
            self.chunks = new_chunks
        
        self.chunks.append(buffer_chunk)
        self.total_added += 1
        
        # Adapt buffer size based on recent patterns
        self._adapt_buffer_size(complexity)
    
    def _analyze_chunk_complexity(self, chunk: BufferChunk) -> float:
        """Analyze complexity of a chunk.
        
        Args:
            chunk: Chunk to analyze
            
        Returns:
            Complexity score (0.0 to 1.0)
        """
        text = chunk.text
        
        # Simple complexity metrics
        factors = []
        
        # Length factor
        length_factor = min(len(text) / 100, 1.0)
        factors.append(length_factor)
        
        # Script diversity factor
        scripts = set()
        for char in text:
            if char.isalpha():
                if ord(char) < 128:
                    scripts.add('latin')
                elif 0x0600 <= ord(char) <= 0x06FF:
                    scripts.add('arabic')
                elif 0x4E00 <= ord(char) <= 0x9FFF:
                    scripts.add('cjk')
                elif 0x0400 <= ord(char) <= 0x04FF:
                    scripts.add('cyrillic')
        
        script_factor = min(len(scripts) / 3, 1.0)
        factors.append(script_factor)
        
        # Punctuation factor
        punct_count = sum(1 for char in text if not char.isalnum() and not char.isspace())
        punct_factor = min(punct_count / max(len(text), 1), 0.5) * 2
        factors.append(punct_factor)
        
        return np.mean(factors) if factors else 0.0
    
    def _adapt_buffer_size(self, chunk_complexity: float) -> None:
        """Adapt buffer size based on complexity and patterns.
        
        Args:
            chunk_complexity: Complexity of current chunk
        """
        # Update recent complexity
        self.recent_complexity_score = (
            self.recent_complexity_score * 0.8 + chunk_complexity * 0.2
        )
        
        # Calculate target size based on complexity
        if self.recent_complexity_score > 0.7:
            # High complexity - increase buffer size
            target_size = min(self.current_size + 5, self.max_size)
        elif self.recent_complexity_score < 0.3:
            # Low complexity - decrease buffer size
            target_size = max(self.current_size - 3, self.min_size)
        else:
            # Medium complexity - maintain size
            target_size = self.current_size
        
        # Gradual adaptation
        if target_size != self.current_size:
            size_diff = target_size - self.current_size
            adaptation_step = max(1, int(abs(size_diff) * self.adaptation_rate))
            
            if size_diff > 0:
                self.current_size = min(self.current_size + adaptation_step, target_size)
            else:
                self.current_size = max(self.current_size - adaptation_step, target_size)
            
            # Record adaptation
            self.adaptation_history.append({
                'timestamp': time.time(),
                'old_size': self.current_size - (adaptation_step if size_diff > 0 else -adaptation_step),
                'new_size': self.current_size,
                'complexity': self.recent_complexity_score,
                'reason': 'high_complexity' if size_diff > 0 else 'low_complexity'
            })
    
    def get_recent_chunks(self, n: int) -> List[BufferChunk]:
        """Get the n most recent chunks.
        
        Args:
            n: Number of recent chunks to return
            
        Returns:
            List of recent chunks
        """
        return list(self.chunks)[-n:] if n <= len(self.chunks) else list(self.chunks)
    
    def get_context_text(self, n: Optional[int] = None) -> str:
        """Get context text from recent chunks.
        
        Args:
            n: Number of chunks for context (None for all)
            
        Returns:
            Combined context text
        """
        if n is None:
            chunks = list(self.chunks)
        else:
            chunks = self.get_recent_chunks(n)
        
        return ' '.join(chunk.text for chunk in chunks)
    
    def clear(self) -> None:
        """Clear the buffer."""
        self.chunks.clear()
        self.recent_complexity_score = 0.0
        self.adaptation_history.clear()
    
    def get_state(self) -> Dict[str, Any]:
        """Get buffer state information.
        
        Returns:
            Buffer state dictionary
        """
        return {
            'size': len(self.chunks),
            'current_size': self.current_size,
            'min_size': self.min_size,
            'max_size': self.max_size,
            'total_added': self.total_added,
            'complexity_score': self.recent_complexity_score,
            'adaptation_count': len(self.adaptation_history),
            'utilization': len(self.chunks) / self.current_size,
            'efficiency': min(self.recent_complexity_score + 0.5, 1.0)
        }
    
    def get_adaptation_history(self) -> List[Dict[str, Any]]:
        """Get buffer adaptation history.
        
        Returns:
            List of adaptation events
        """
        return list(self.adaptation_history)


def main():
    """Example usage of buffer managers."""
    print("🔄 Buffer Management Example")
    print("=" * 40)
    
    # Test different buffer types
    buffers = {
        'circular': CircularBuffer(max_size=10),
        'sliding': SlidingWindowBuffer(max_size=10, overlap_ratio=0.3),
        'adaptive': AdaptiveBuffer(initial_size=8, min_size=5, max_size=15)
    }
    
    # Sample chunks
    test_chunks = [
        ("Hello world", 1.0, 1),
        ("¿Cómo estás?", 1.1, 2),
        ("I am fine", 1.2, 3),
        ("Muy bien gracias", 1.3, 4),
        ("What are you doing?", 1.4, 5),
        ("Estoy trabajando", 1.5, 6),
        ("That's great", 1.6, 7),
        ("Sí, es genial", 1.7, 8),
        ("Let's continue", 1.8, 9),
        ("Vamos a continuar", 1.9, 10),
        ("More text here", 2.0, 11),
        ("Más texto aquí", 2.1, 12)
    ]
    
    # Create mock chunk objects
    class MockChunk:
        def __init__(self, text, timestamp, chunk_id):
            self.text = text
            self.timestamp = timestamp
            self.chunk_id = chunk_id
            self.speaker_id = f"speaker_{chunk_id % 2}"
    
    chunks = [MockChunk(text, ts, cid) for text, ts, cid in test_chunks]
    
    print("\n🧪 Testing buffer types:")
    
    for buffer_name, buffer in buffers.items():
        print(f"\n--- {buffer_name.title()} Buffer ---")
        
        # Add chunks
        for chunk in chunks:
            buffer.add_chunk(chunk)
        
        # Show state
        state = buffer.get_state()
        print(f"Final state: {state}")
        
        # Show recent chunks
        recent = buffer.get_recent_chunks(3)
        print(f"Recent chunks: {[c.text for c in recent]}")
        
        # Show context
        context = buffer.get_context_text(3)
        print(f"Context: '{context}'")
        
        # Special info for adaptive buffer
        if buffer_name == 'adaptive':
            history = buffer.get_adaptation_history()
            if history:
                print(f"Adaptations: {len(history)}")
                for event in history[-2:]:  # Show last 2 adaptations
                    print(f"  {event['old_size']} → {event['new_size']} ({event['reason']})")
    
    print("\n✓ Buffer management example completed")


if __name__ == "__main__":
    main()