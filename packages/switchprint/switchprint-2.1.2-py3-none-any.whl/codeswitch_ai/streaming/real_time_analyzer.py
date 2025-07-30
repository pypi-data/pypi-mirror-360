#!/usr/bin/env python3
"""Real-time conversation analysis for streaming detection."""

import time
import numpy as np
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum

from ..analysis.temporal_analysis import TemporalCodeSwitchAnalyzer, TemporalPattern
from ..detection.switch_point_refiner import SwitchPointRefiner


class ConversationPhase(Enum):
    """Phases of conversation analysis."""
    STARTUP = "startup"
    ACTIVE = "active"
    TRANSITIONAL = "transitional"
    STABLE = "stable"
    ENDING = "ending"


@dataclass
class ConversationState:
    """Current state of the conversation."""
    phase: ConversationPhase
    dominant_language: str
    language_distribution: Dict[str, float]
    switch_frequency: float
    participant_count: int
    conversation_duration: float
    activity_level: float
    coherence_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['phase'] = self.phase.value
        return result


@dataclass
class LiveDetectionResult:
    """Real-time detection result with conversation context."""
    chunk_id: int
    text: str
    timestamp: float
    detected_languages: List[str]
    confidence: float
    switch_detected: bool
    conversation_state: ConversationState
    temporal_patterns: Dict[str, Any]
    switch_points: Optional[List[Dict[str, Any]]] = None
    participant_analysis: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class RealTimeAnalyzer:
    """Real-time conversation analyzer for streaming detection."""
    
    def __init__(self, 
                 temporal_window_size: int = 20,
                 enable_switch_refinement: bool = True,
                 enable_participant_tracking: bool = True):
        """Initialize real-time analyzer.
        
        Args:
            temporal_window_size: Size of temporal analysis window
            enable_switch_refinement: Enable detailed switch point analysis
            enable_participant_tracking: Enable per-participant analysis
        """
        self.temporal_window_size = temporal_window_size
        self.enable_switch_refinement = enable_switch_refinement
        self.enable_participant_tracking = enable_participant_tracking
        
        # Initialize components
        self.temporal_analyzer = TemporalCodeSwitchAnalyzer()
        if enable_switch_refinement:
            self.switch_refiner = SwitchPointRefiner()
        
        # Conversation state
        self.conversation_history = deque(maxlen=temporal_window_size * 2)
        self.current_state = None
        self.session_start_time = None
        self.chunk_counter = 0
        
        # Participant tracking
        self.participants = {}  # speaker_id -> participant info
        self.language_usage = defaultdict(lambda: defaultdict(float))
        
        # Pattern tracking
        self.recent_patterns = deque(maxlen=10)
        self.switch_history = deque(maxlen=50)
        
        print("🎯 Real-time analyzer initialized")
    
    def start_session(self) -> None:
        """Start a new conversation session."""
        self.session_start_time = time.time()
        self.chunk_counter = 0
        self.conversation_history.clear()
        self.participants.clear()
        self.language_usage.clear()
        self.recent_patterns.clear()
        self.switch_history.clear()
        
        # Initialize conversation state
        self.current_state = ConversationState(
            phase=ConversationPhase.STARTUP,
            dominant_language="unknown",
            language_distribution={},
            switch_frequency=0.0,
            participant_count=0,
            conversation_duration=0.0,
            activity_level=0.0,
            coherence_score=0.0
        )
        
        print("🚀 Real-time analysis session started")
    
    def analyze_chunk(self, 
                     text: str,
                     detected_languages: List[str],
                     confidence: float,
                     speaker_id: Optional[str] = None,
                     switch_detected: bool = False) -> LiveDetectionResult:
        """Analyze a chunk in real-time context.
        
        Args:
            text: Text content
            detected_languages: Detected languages
            confidence: Detection confidence
            speaker_id: Optional speaker identifier
            switch_detected: Whether a switch was detected
            
        Returns:
            Live detection result with conversation context
        """
        timestamp = time.time()
        self.chunk_counter += 1
        
        # Create chunk record
        chunk_record = {
            'chunk_id': self.chunk_counter,
            'text': text,
            'timestamp': timestamp,
            'detected_languages': detected_languages,
            'confidence': confidence,
            'speaker_id': speaker_id or 'unknown',
            'switch_detected': switch_detected
        }
        
        # Add to conversation history
        self.conversation_history.append(chunk_record)
        
        # Update participant tracking
        if self.enable_participant_tracking and speaker_id:
            self._update_participant_tracking(speaker_id, detected_languages, confidence)
        
        # Update conversation state
        self._update_conversation_state()
        
        # Analyze temporal patterns
        temporal_patterns = self._analyze_temporal_patterns()
        
        # Analyze switch points if enabled
        switch_points = None
        if self.enable_switch_refinement and text.strip():
            switch_points = self._analyze_switch_points(text)
        
        # Analyze participant patterns
        participant_analysis = None
        if self.enable_participant_tracking:
            participant_analysis = self._analyze_participant_patterns()
        
        # Create result
        result = LiveDetectionResult(
            chunk_id=self.chunk_counter,
            text=text,
            timestamp=timestamp,
            detected_languages=detected_languages,
            confidence=confidence,
            switch_detected=switch_detected,
            conversation_state=self.current_state,
            temporal_patterns=temporal_patterns,
            switch_points=switch_points,
            participant_analysis=participant_analysis
        )
        
        # Update switch history
        if switch_detected:
            self.switch_history.append({
                'timestamp': timestamp,
                'from_lang': self._get_previous_language(),
                'to_lang': detected_languages[0] if detected_languages else 'unknown',
                'speaker_id': speaker_id,
                'confidence': confidence
            })
        
        return result
    
    def _update_participant_tracking(self, 
                                   speaker_id: str, 
                                   languages: List[str], 
                                   confidence: float) -> None:
        """Update tracking for a specific participant.
        
        Args:
            speaker_id: Speaker identifier
            languages: Detected languages
            confidence: Detection confidence
        """
        if speaker_id not in self.participants:
            self.participants[speaker_id] = {
                'first_seen': time.time(),
                'chunk_count': 0,
                'languages_used': set(),
                'primary_language': 'unknown',
                'switch_count': 0,
                'last_language': 'unknown'
            }
        
        participant = self.participants[speaker_id]
        participant['chunk_count'] += 1
        
        if languages:
            primary_lang = languages[0]
            participant['languages_used'].update(languages)
            
            # Update language usage statistics
            self.language_usage[speaker_id][primary_lang] += confidence
            
            # Check for participant switch
            if (participant['last_language'] != 'unknown' and 
                participant['last_language'] != primary_lang):
                participant['switch_count'] += 1
            
            participant['last_language'] = primary_lang
            
            # Update primary language (most used)
            usage_counts = self.language_usage[speaker_id]
            if usage_counts:
                participant['primary_language'] = max(usage_counts.keys(), 
                                                    key=usage_counts.get)
    
    def _update_conversation_state(self) -> None:
        """Update the current conversation state."""
        if not self.conversation_history:
            return
        
        current_time = time.time()
        session_duration = current_time - self.session_start_time if self.session_start_time else 0
        
        # Update duration
        self.current_state.conversation_duration = session_duration
        
        # Update participant count
        speakers = set(chunk['speaker_id'] for chunk in self.conversation_history 
                      if chunk['speaker_id'] != 'unknown')
        self.current_state.participant_count = len(speakers)
        
        # Calculate language distribution
        lang_counts = defaultdict(float)
        total_confidence = 0
        
        for chunk in self.conversation_history:
            if chunk['detected_languages']:
                lang = chunk['detected_languages'][0]
                confidence = chunk['confidence']
                lang_counts[lang] += confidence
                total_confidence += confidence
        
        if total_confidence > 0:
            self.current_state.language_distribution = {
                lang: count / total_confidence 
                for lang, count in lang_counts.items()
            }
            
            # Find dominant language
            self.current_state.dominant_language = max(
                lang_counts.keys(), key=lang_counts.get
            )
        
        # Calculate switch frequency (switches per minute)
        switch_count = len(self.switch_history)
        if session_duration > 0:
            self.current_state.switch_frequency = (switch_count / session_duration) * 60
        
        # Calculate activity level (chunks per minute)
        if session_duration > 0:
            self.current_state.activity_level = (len(self.conversation_history) / session_duration) * 60
        
        # Calculate coherence score (simplified)
        self.current_state.coherence_score = self._calculate_coherence_score()
        
        # Update conversation phase
        self._update_conversation_phase()
    
    def _calculate_coherence_score(self) -> float:
        """Calculate conversation coherence score.
        
        Returns:
            Coherence score (0.0 to 1.0)
        """
        if len(self.conversation_history) < 3:
            return 0.5  # Neutral for too little data
        
        factors = []
        
        # Language consistency factor
        recent_chunks = list(self.conversation_history)[-10:]
        languages = [chunk['detected_languages'][0] if chunk['detected_languages'] else 'unknown' 
                    for chunk in recent_chunks]
        
        # Calculate language entropy
        lang_counts = defaultdict(int)
        for lang in languages:
            lang_counts[lang] += 1
        
        if len(lang_counts) > 0:
            total = len(languages)
            entropy = 0
            for count in lang_counts.values():
                p = count / total
                if p > 0:
                    entropy -= p * np.log2(p)
            
            max_entropy = np.log2(len(lang_counts)) if len(lang_counts) > 1 else 1
            consistency_factor = 1 - (entropy / max_entropy) if max_entropy > 0 else 1
            factors.append(consistency_factor)
        
        # Confidence factor
        confidences = [chunk['confidence'] for chunk in recent_chunks]
        if confidences:
            avg_confidence = np.mean(confidences)
            factors.append(avg_confidence)
        
        # Temporal regularity factor
        if len(recent_chunks) >= 3:
            timestamps = [chunk['timestamp'] for chunk in recent_chunks]
            intervals = np.diff(timestamps)
            if len(intervals) > 1:
                interval_std = np.std(intervals)
                interval_mean = np.mean(intervals)
                regularity = 1 - min(interval_std / max(interval_mean, 0.1), 1.0)
                factors.append(regularity)
        
        return np.mean(factors) if factors else 0.5
    
    def _update_conversation_phase(self) -> None:
        """Update the conversation phase based on current state."""
        duration = self.current_state.conversation_duration
        activity = self.current_state.activity_level
        switch_freq = self.current_state.switch_frequency
        
        if duration < 30:  # First 30 seconds
            self.current_state.phase = ConversationPhase.STARTUP
        elif activity > 20 and switch_freq > 2:  # High activity and switching
            self.current_state.phase = ConversationPhase.TRANSITIONAL
        elif activity > 10 and switch_freq < 1:  # Active but stable
            self.current_state.phase = ConversationPhase.STABLE
        elif activity > 5:  # Moderate activity
            self.current_state.phase = ConversationPhase.ACTIVE
        else:  # Low activity
            self.current_state.phase = ConversationPhase.ENDING
    
    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in conversation.
        
        Returns:
            Temporal pattern analysis
        """
        if len(self.conversation_history) < 3:
            return {}
        
        try:
            # Convert to format expected by temporal analyzer
            messages = [
                {
                    'text': chunk['text'],
                    'timestamp': chunk['timestamp'],
                    'speaker_id': chunk['speaker_id'],
                    'detected_languages': chunk['detected_languages']
                }
                for chunk in list(self.conversation_history)[-self.temporal_window_size:]
            ]
            
            # Analyze temporal statistics
            temporal_stats = self.temporal_analyzer.analyze_conversation_history(
                messages, session_id="realtime"
            )
            
            # Extract key patterns
            patterns = {
                'trend': temporal_stats.pattern_trend,
                'frequency': temporal_stats.switch_frequency,
                'dominant_pattern': None,
                'pattern_strength': 0.0,
                'cyclical_period': None
            }
            
            if temporal_stats.dominant_pattern:
                patterns['dominant_pattern'] = temporal_stats.dominant_pattern.pattern_type
                patterns['pattern_strength'] = temporal_stats.dominant_pattern.strength
                
                if temporal_stats.dominant_pattern.pattern_type == 'cyclical':
                    patterns['cyclical_period'] = getattr(
                        temporal_stats.dominant_pattern, 'period', None
                    )
            
            # Add to recent patterns for trend analysis
            self.recent_patterns.append(patterns)
            
            return patterns
            
        except Exception as e:
            print(f"⚠ Temporal analysis failed: {e}")
            return {}
    
    def _analyze_switch_points(self, text: str) -> List[Dict[str, Any]]:
        """Analyze switch points in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of switch point analyses
        """
        if not self.enable_switch_refinement or not text.strip():
            return []
        
        try:
            # Get user languages from current state
            user_languages = list(self.current_state.language_distribution.keys())
            
            # Refine switch points
            refinement = self.switch_refiner.refine_switch_points(
                text, user_languages=user_languages
            )
            
            # Convert to simple format
            switch_points = []
            for switch in refinement.refined_switches:
                switch_points.append({
                    'position': switch.position,
                    'from_language': switch.from_language,
                    'to_language': switch.to_language,
                    'confidence': switch.confidence,
                    'boundary_type': switch.boundary_type,
                    'context_before': switch.context_before,
                    'context_after': switch.context_after
                })
            
            return switch_points
            
        except Exception as e:
            print(f"⚠ Switch point analysis failed: {e}")
            return []
    
    def _analyze_participant_patterns(self) -> Dict[str, Any]:
        """Analyze patterns across participants.
        
        Returns:
            Participant pattern analysis
        """
        if not self.enable_participant_tracking or not self.participants:
            return {}
        
        analysis = {
            'total_participants': len(self.participants),
            'active_participants': 0,
            'multilingual_participants': 0,
            'switch_patterns': {},
            'language_preferences': {},
            'interaction_patterns': {}
        }
        
        current_time = time.time()
        
        for speaker_id, info in self.participants.items():
            # Check if participant is active (spoke in last 60 seconds)
            time_since_seen = current_time - info.get('last_seen', info['first_seen'])
            if time_since_seen < 60:
                analysis['active_participants'] += 1
            
            # Check if multilingual
            if len(info['languages_used']) > 1:
                analysis['multilingual_participants'] += 1
            
            # Store language preferences
            if speaker_id in self.language_usage:
                total_usage = sum(self.language_usage[speaker_id].values())
                if total_usage > 0:
                    analysis['language_preferences'][speaker_id] = {
                        lang: usage / total_usage 
                        for lang, usage in self.language_usage[speaker_id].items()
                    }
            
            # Store switch patterns
            analysis['switch_patterns'][speaker_id] = {
                'switch_count': info['switch_count'],
                'switch_rate': info['switch_count'] / max(info['chunk_count'], 1),
                'primary_language': info['primary_language']
            }
        
        return analysis
    
    def _get_previous_language(self) -> str:
        """Get the language from the previous chunk.
        
        Returns:
            Previous language or 'unknown'
        """
        if len(self.conversation_history) >= 2:
            prev_chunk = list(self.conversation_history)[-2]
            if prev_chunk['detected_languages']:
                return prev_chunk['detected_languages'][0]
        return 'unknown'
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session.
        
        Returns:
            Session summary
        """
        if not self.current_state:
            return {}
        
        summary = {
            'conversation_state': self.current_state.to_dict(),
            'total_chunks': len(self.conversation_history),
            'total_switches': len(self.switch_history),
            'participants': dict(self.participants),
            'language_usage': dict(self.language_usage),
            'recent_patterns': list(self.recent_patterns)[-5:],  # Last 5 patterns
            'session_duration': self.current_state.conversation_duration
        }
        
        return summary
    
    def end_session(self) -> Dict[str, Any]:
        """End the current session and return final summary.
        
        Returns:
            Final session summary
        """
        summary = self.get_session_summary()
        
        # Clear session data
        self.conversation_history.clear()
        self.participants.clear()
        self.language_usage.clear()
        self.recent_patterns.clear()
        self.switch_history.clear()
        self.current_state = None
        self.session_start_time = None
        
        print("🏁 Real-time analysis session ended")
        return summary


def main():
    """Example usage of real-time analyzer."""
    print("🎯 Real-time Analyzer Example")
    print("=" * 40)
    
    # Initialize analyzer
    analyzer = RealTimeAnalyzer(
        temporal_window_size=15,
        enable_switch_refinement=True,
        enable_participant_tracking=True
    )
    
    # Start session
    analyzer.start_session()
    
    # Simulate conversation chunks
    conversation_chunks = [
        ("Hello everyone", ["english"], 0.9, "speaker_1", False),
        ("¿Cómo están todos?", ["spanish"], 0.85, "speaker_2", True),
        ("I'm doing well", ["english"], 0.88, "speaker_1", True),
        ("Muy bien también", ["spanish"], 0.82, "speaker_2", True),
        ("Let's start the meeting", ["english"], 0.91, "speaker_1", True),
        ("Sí, empecemos", ["spanish"], 0.87, "speaker_2", True),
        ("The first topic is important", ["english"], 0.93, "speaker_1", True),
        ("Es muy importante indeed", ["spanish", "english"], 0.75, "speaker_2", True),
    ]
    
    print("\n🔄 Processing conversation chunks:")
    
    for i, (text, languages, confidence, speaker, switch) in enumerate(conversation_chunks):
        print(f"\nChunk {i+1}: '{text}' ({speaker})")
        
        # Analyze chunk
        result = analyzer.analyze_chunk(
            text=text,
            detected_languages=languages,
            confidence=confidence,
            speaker_id=speaker,
            switch_detected=switch
        )
        
        # Show key results
        state = result.conversation_state
        print(f"  Phase: {state.phase.value}")
        print(f"  Dominant language: {state.dominant_language}")
        print(f"  Switch frequency: {state.switch_frequency:.2f}/min")
        print(f"  Activity level: {state.activity_level:.1f} chunks/min")
        print(f"  Coherence: {state.coherence_score:.3f}")
        
        if result.switch_points:
            print(f"  Switch points: {len(result.switch_points)}")
        
        if result.participant_analysis:
            active = result.participant_analysis['active_participants']
            multilingual = result.participant_analysis['multilingual_participants']
            print(f"  Participants: {active} active, {multilingual} multilingual")
        
        # Small delay to simulate real-time
        time.sleep(0.2)
    
    # Get final summary
    summary = analyzer.end_session()
    
    print("\n📈 Session Summary:")
    print(f"  Total chunks: {summary['total_chunks']}")
    print(f"  Total switches: {summary['total_switches']}")
    print(f"  Session duration: {summary['session_duration']:.1f}s")
    print(f"  Participants: {list(summary['participants'].keys())}")
    
    if summary['language_usage']:
        print("  Language usage:")
        for speaker, usage in summary['language_usage'].items():
            print(f"    {speaker}: {dict(usage)}")
    
    print("\n✓ Real-time analyzer example completed")


if __name__ == "__main__":
    main()