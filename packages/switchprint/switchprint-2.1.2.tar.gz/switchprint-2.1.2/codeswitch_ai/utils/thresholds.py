#!/usr/bin/env python3
"""Dynamic threshold profiles for different use cases."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional


class DetectionMode(Enum):
    """Detection mode enumeration."""
    HIGH_PRECISION = "high_precision"
    HIGH_RECALL = "high_recall"
    BALANCED = "balanced"
    CUSTOM = "custom"


@dataclass
class ThresholdProfile:
    """Threshold configuration profile."""
    name: str
    description: str
    
    # Primary language confidence thresholds
    monolingual_min_confidence: float
    multilingual_primary_confidence: float
    
    # Secondary language thresholds
    multilingual_secondary_confidence: float
    
    # Language inclusion threshold
    min_inclusion_threshold: float
    
    # Warning threshold for low confidence single-language predictions
    warning_threshold: float


class ThresholdConfig:
    """Manages threshold configurations for different use cases."""
    
    PROFILES = {
        DetectionMode.HIGH_PRECISION: ThresholdProfile(
            name="High Precision",
            description="Strict thresholds to minimize false positives",
            monolingual_min_confidence=0.8,
            multilingual_primary_confidence=0.7,
            multilingual_secondary_confidence=0.5,
            min_inclusion_threshold=0.25,
            warning_threshold=0.6
        ),
        
        DetectionMode.BALANCED: ThresholdProfile(
            name="Balanced",
            description="Balanced precision and recall for general use",
            monolingual_min_confidence=0.6,
            multilingual_primary_confidence=0.5,
            multilingual_secondary_confidence=0.3,
            min_inclusion_threshold=0.15,
            warning_threshold=0.5
        ),
        
        DetectionMode.HIGH_RECALL: ThresholdProfile(
            name="High Recall", 
            description="Lower thresholds to catch more languages",
            monolingual_min_confidence=0.4,
            multilingual_primary_confidence=0.3,
            multilingual_secondary_confidence=0.2,
            min_inclusion_threshold=0.1,
            warning_threshold=0.3
        )
    }
    
    def __init__(self, mode: DetectionMode = DetectionMode.BALANCED, 
                 custom_profile: Optional[ThresholdProfile] = None):
        """Initialize threshold configuration.
        
        Args:
            mode: Detection mode to use
            custom_profile: Custom threshold profile (used if mode is CUSTOM)
        """
        self.mode = mode
        
        if mode == DetectionMode.CUSTOM and custom_profile:
            self.profile = custom_profile
        else:
            self.profile = self.PROFILES.get(mode, self.PROFILES[DetectionMode.BALANCED])
    
    def get_inclusion_threshold(self) -> float:
        """Get minimum inclusion threshold."""
        return self.profile.min_inclusion_threshold
    
    def validate_confidence(self, detected_languages: list, confidence: float, text_length: int = None) -> Dict[str, Any]:
        """Validate confidence levels and return warnings/status.
        
        Args:
            detected_languages: List of detected languages
            confidence: Primary confidence score
            text_length: Number of tokens/words in input text
            
        Returns:
            Dictionary with validation results
        """
        # Handle empty cases
        if not detected_languages and confidence == 0.0:
            return {
                "is_valid": True,
                "warnings": ["No language detected - empty or unrecognizable input"],
                "quality": "empty",
                "needs_review": False,
                "text_length_category": "empty",
                "confidence_adjusted": 0.0
            }
        
        is_monolingual = len(detected_languages) == 1
        is_multilingual = len(detected_languages) > 1
        is_short_text = text_length is not None and text_length < 5
        
        validation = {
            "is_valid": True,
            "warnings": [],
            "quality": "good",
            "needs_review": False,
            "text_length_category": "short" if is_short_text else ("medium" if text_length and text_length < 20 else "long"),
            "confidence_adjusted": confidence
        }
        
        # Add short text advisory
        if is_short_text:
            validation["warnings"].append(
                f"Short text ({text_length} tokens) may yield unreliable confidence scores"
            )
            # Adjust confidence expectations for short text
            adjusted_threshold = self.profile.warning_threshold * 0.7  # Lower expectations
            validation["confidence_adjusted"] = confidence / 0.7  # Boost confidence interpretation
        else:
            adjusted_threshold = self.profile.warning_threshold
        
        if is_monolingual:
            if confidence < adjusted_threshold:
                validation["warnings"].append(
                    f"Low confidence ({confidence:.3f}) for single-language detection"
                )
                validation["needs_review"] = True
                validation["quality"] = "poor" if confidence < 0.3 else "fair"
            
            if confidence >= self.profile.monolingual_min_confidence:
                validation["quality"] = "excellent"
            elif confidence >= self.profile.warning_threshold:
                validation["quality"] = "good"
        
        elif is_multilingual:
            if confidence < self.profile.multilingual_primary_confidence:
                validation["warnings"].append(
                    f"Low primary confidence ({confidence:.3f}) for multilingual text"
                )
                validation["quality"] = "fair"
            
            if confidence >= self.profile.multilingual_primary_confidence * 1.2:
                validation["quality"] = "excellent"
            elif confidence >= self.profile.multilingual_primary_confidence:
                validation["quality"] = "good"
        
        else:  # No languages detected
            validation["is_valid"] = False
            validation["warnings"].append("No languages detected")
            validation["quality"] = "failed"
            validation["needs_review"] = True
        
        return validation
    
    def get_profile_info(self) -> Dict[str, Any]:
        """Get current profile information."""
        return {
            "mode": self.mode.value,
            "name": self.profile.name,
            "description": self.profile.description,
            "thresholds": {
                "monolingual_min": self.profile.monolingual_min_confidence,
                "multilingual_primary": self.profile.multilingual_primary_confidence,
                "multilingual_secondary": self.profile.multilingual_secondary_confidence,
                "min_inclusion": self.profile.min_inclusion_threshold,
                "warning": self.profile.warning_threshold
            }
        }
    
    @classmethod
    def create_custom_profile(cls, 
                            name: str,
                            monolingual_min: float = 0.6,
                            multilingual_primary: float = 0.5,
                            multilingual_secondary: float = 0.3,
                            min_inclusion: float = 0.15,
                            warning_threshold: float = 0.5) -> 'ThresholdConfig':
        """Create custom threshold configuration.
        
        Args:
            name: Name for the custom profile
            monolingual_min: Minimum confidence for single-language detection
            multilingual_primary: Minimum confidence for primary language in multilingual text
            multilingual_secondary: Minimum confidence for secondary languages
            min_inclusion: Minimum threshold for language inclusion
            warning_threshold: Threshold below which warnings are issued
            
        Returns:
            ThresholdConfig with custom profile
        """
        custom_profile = ThresholdProfile(
            name=name,
            description="Custom user-defined profile",
            monolingual_min_confidence=monolingual_min,
            multilingual_primary_confidence=multilingual_primary,
            multilingual_secondary_confidence=multilingual_secondary,
            min_inclusion_threshold=min_inclusion,
            warning_threshold=warning_threshold
        )
        
        return cls(DetectionMode.CUSTOM, custom_profile)
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'ThresholdConfig':
        """Create threshold config from dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            ThresholdConfig instance
        """
        mode_str = config.get("mode", "balanced")
        
        try:
            mode = DetectionMode(mode_str)
        except ValueError:
            mode = DetectionMode.BALANCED
        
        if mode == DetectionMode.CUSTOM:
            custom_config = config.get("custom", {})
            return cls.create_custom_profile(
                name=custom_config.get("name", "Custom"),
                monolingual_min=custom_config.get("monolingual_min", 0.6),
                multilingual_primary=custom_config.get("multilingual_primary", 0.5),
                multilingual_secondary=custom_config.get("multilingual_secondary", 0.3),
                min_inclusion=custom_config.get("min_inclusion", 0.15),
                warning_threshold=custom_config.get("warning_threshold", 0.5)
            )
        
        return cls(mode)