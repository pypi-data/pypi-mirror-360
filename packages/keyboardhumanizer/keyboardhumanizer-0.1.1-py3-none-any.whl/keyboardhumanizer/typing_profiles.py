"""
Typing Profiles - Different Human Typing Behavior Patterns
Defines realistic typing characteristics for different types of users
"""

import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class TypingCharacteristics:
    """Defines typing behavior characteristics"""
    base_wpm: int = 45                    # Base words per minute
    wpm_variance: int = 15                # Speed variance
    error_rate: float = 0.02              # Error rate per character
    correction_rate: float = 0.8          # Rate of error correction
    thinking_pause_freq: float = 0.1      # Frequency of thinking pauses
    burst_typing: bool = True             # Types in bursts vs steady
    copy_paste_likelihood: float = 0.2    # Likelihood to use copy-paste
    fatigue_sensitivity: float = 1.0      # How quickly fatigue builds up
    accuracy_focus: bool = False          # Prioritizes accuracy over speed


class TypingProfile(ABC):
    """Abstract base class for typing profiles"""
    
    def __init__(self):
        self.characteristics = self.get_characteristics()
        self.name = self.__class__.__name__
        
    @abstractmethod
    def get_characteristics(self) -> TypingCharacteristics:
        """Get the typing characteristics for this profile"""
        pass
    
    @abstractmethod
    def get_error_patterns(self) -> Dict[str, float]:
        """Get specific error patterns for this profile"""
        pass
    
    @abstractmethod
    def get_rhythm_patterns(self) -> Dict[str, Any]:
        """Get typing rhythm patterns"""
        pass
    
    def apply_to_engine(self, engine):
        """Apply this profile's characteristics to a typing engine"""
        char = self.characteristics
        
        engine.base_wpm = char.base_wpm
        engine.wpm_variance = char.wpm_variance
        engine.error_rate = char.error_rate
        engine.correction_rate = char.correction_rate
        engine.burst_typing = char.burst_typing
        
        # Apply error patterns
        error_patterns = self.get_error_patterns()
        if hasattr(engine, 'error_patterns'):
            engine.error_patterns.update(error_patterns)
            
        print(f"Applied {self.name} profile: {char.base_wpm} WPM, "
              f"{char.error_rate:.1%} error rate")


class ProfessionalProfile(TypingProfile):
    """Professional typist - fast, accurate, efficient"""
    
    def get_characteristics(self) -> TypingCharacteristics:
        return TypingCharacteristics(
            base_wpm=75,
            wpm_variance=20,
            error_rate=0.008,  # Very low error rate
            correction_rate=0.95,  # High correction rate
            thinking_pause_freq=0.05,  # Minimal thinking pauses
            burst_typing=True,
            copy_paste_likelihood=0.4,  # Efficient use of copy-paste
            fatigue_sensitivity=0.6,  # Resistant to fatigue
            accuracy_focus=True
        )
    
    def get_error_patterns(self) -> Dict[str, float]:
        return {
            'substitution': 0.4,     # Most errors are substitutions
            'insertion': 0.2,        # Few insertions
            'deletion': 0.1,         # Very few deletions
            'transposition': 0.3     # Some transpositions
        }
    
    def get_rhythm_patterns(self) -> Dict[str, Any]:
        return {
            'consistent_pace': True,
            'pause_after_punctuation': True,
            'faster_on_common_words': True,
            'efficient_corrections': True
        }


class CasualProfile(TypingProfile):
    """Casual user - moderate speed, occasional errors"""
    
    def get_characteristics(self) -> TypingCharacteristics:
        return TypingCharacteristics(
            base_wpm=45,
            wpm_variance=20,
            error_rate=0.025,
            correction_rate=0.75,
            thinking_pause_freq=0.15,
            burst_typing=True,
            copy_paste_likelihood=0.15,
            fatigue_sensitivity=1.0,
            accuracy_focus=False
        )
    
    def get_error_patterns(self) -> Dict[str, float]:
        return {
            'substitution': 0.5,
            'insertion': 0.2,
            'deletion': 0.15,
            'transposition': 0.15
        }
    
    def get_rhythm_patterns(self) -> Dict[str, Any]:
        return {
            'variable_pace': True,
            'thinking_pauses': True,
            'occasional_burst': True,
            'moderate_corrections': True
        }


class BeginnerProfile(TypingProfile):
    """Beginner - slow, hunt-and-peck style, many errors"""
    
    def get_characteristics(self) -> TypingCharacteristics:
        return TypingCharacteristics(
            base_wpm=20,
            wpm_variance=10,
            error_rate=0.08,  # High error rate
            correction_rate=0.9,  # High correction rate (notices errors)
            thinking_pause_freq=0.3,  # Frequent pauses
            burst_typing=False,  # Steady, careful typing
            copy_paste_likelihood=0.05,  # Rarely uses copy-paste
            fatigue_sensitivity=1.5,  # Gets tired quickly
            accuracy_focus=True  # Focuses on accuracy over speed
        )
    
    def get_error_patterns(self) -> Dict[str, float]:
        return {
            'substitution': 0.6,  # Many wrong keys
            'insertion': 0.15,
            'deletion': 0.2,  # Often misses keys
            'transposition': 0.05  # Rare transpositions
        }
    
    def get_rhythm_patterns(self) -> Dict[str, Any]:
        return {
            'hunt_and_peck': True,
            'long_pauses': True,
            'careful_corrections': True,
            'slow_special_chars': True,
            'frequent_backspacing': True
        }


class GamingProfile(TypingProfile):
    """Gamer - fast on familiar terms, good with shortcuts"""
    
    def get_characteristics(self) -> TypingCharacteristics:
        return TypingCharacteristics(
            base_wpm=60,
            wpm_variance=25,  # Highly variable speed
            error_rate=0.03,
            correction_rate=0.6,  # Often doesn't correct in games
            thinking_pause_freq=0.05,
            burst_typing=True,
            copy_paste_likelihood=0.3,  # Good with shortcuts
            fatigue_sensitivity=0.8,
            accuracy_focus=False
        )
    
    def get_error_patterns(self) -> Dict[str, float]:
        return {
            'substitution': 0.3,
            'insertion': 0.4,  # Many insertions from fast typing
            'deletion': 0.1,
            'transposition': 0.2
        }
    
    def get_rhythm_patterns(self) -> Dict[str, Any]:
        return {
            'burst_on_familiar': True,
            'fast_shortcuts': True,
            'less_correction': True,
            'efficient_navigation': True
        }


class ProgrammerProfile(TypingProfile):
    """Programmer - excellent with symbols, variable speed"""
    
    def get_characteristics(self) -> TypingCharacteristics:
        return TypingCharacteristics(
            base_wpm=65,
            wpm_variance=30,  # Very variable (fast on code, slow on comments)
            error_rate=0.015,
            correction_rate=0.85,
            thinking_pause_freq=0.2,  # Pauses to think about logic
            burst_typing=True,
            copy_paste_likelihood=0.5,  # Heavy copy-paste use
            fatigue_sensitivity=0.7,
            accuracy_focus=True
        )
    
    def get_error_patterns(self) -> Dict[str, float]:
        return {
            'substitution': 0.35,
            'insertion': 0.25,
            'deletion': 0.2,
            'transposition': 0.2
        }
    
    def get_rhythm_patterns(self) -> Dict[str, Any]:
        return {
            'fast_on_keywords': True,
            'careful_with_syntax': True,
            'frequent_copypaste': True,
            'thinking_pauses': True,
            'excellent_with_symbols': True
        }


class ElderlyProfile(TypingProfile):
    """Elderly user - slow, careful, prone to fatigue"""
    
    def get_characteristics(self) -> TypingCharacteristics:
        return TypingCharacteristics(
            base_wpm=25,
            wpm_variance=8,
            error_rate=0.05,
            correction_rate=0.95,  # Very careful about corrections
            thinking_pause_freq=0.25,
            burst_typing=False,
            copy_paste_likelihood=0.08,
            fatigue_sensitivity=2.0,  # Gets tired quickly
            accuracy_focus=True
        )
    
    def get_error_patterns(self) -> Dict[str, float]:
        return {
            'substitution': 0.5,
            'insertion': 0.1,
            'deletion': 0.35,  # Often doesn't press keys hard enough
            'transposition': 0.05
        }
    
    def get_rhythm_patterns(self) -> Dict[str, Any]:
        return {
            'very_careful': True,
            'long_pauses': True,
            'slow_special_chars': True,
            'frequent_checking': True,
            'fatigue_breaks': True
        }


class MobileProfile(TypingProfile):
    """Mobile/touchscreen typing simulation"""
    
    def get_characteristics(self) -> TypingCharacteristics:
        return TypingCharacteristics(
            base_wpm=35,
            wpm_variance=15,
            error_rate=0.06,  # Higher error rate on mobile
            correction_rate=0.7,  # Autocorrect helps
            thinking_pause_freq=0.1,
            burst_typing=False,
            copy_paste_likelihood=0.25,
            fatigue_sensitivity=1.2,
            accuracy_focus=False
        )
    
    def get_error_patterns(self) -> Dict[str, float]:
        return {
            'substitution': 0.7,  # Adjacent key presses common
            'insertion': 0.1,
            'deletion': 0.15,
            'transposition': 0.05
        }
    
    def get_rhythm_patterns(self) -> Dict[str, Any]:
        return {
            'thumb_typing': True,
            'autocorrect_reliance': True,
            'swipe_gestures': True,
            'frequent_corrections': True
        }


# Profile registry for easy access
PROFILE_REGISTRY = {
    'professional': ProfessionalProfile,
    'casual': CasualProfile,
    'beginner': BeginnerProfile,
    'gaming': GamingProfile,
    'programmer': ProgrammerProfile,
    'elderly': ElderlyProfile,
    'mobile': MobileProfile
}


def get_profile(profile_name: str) -> Optional[TypingProfile]:
    """Get a typing profile by name"""
    profile_class = PROFILE_REGISTRY.get(profile_name.lower())
    return profile_class() if profile_class else None


def list_available_profiles() -> List[str]:
    """List all available typing profiles"""
    return list(PROFILE_REGISTRY.keys())


def get_random_profile() -> TypingProfile:
    """Get a random typing profile"""
    profile_name = random.choice(list(PROFILE_REGISTRY.keys()))
    return PROFILE_REGISTRY[profile_name]()


def create_custom_profile(name: str, characteristics: TypingCharacteristics) -> TypingProfile:
    """Create a custom typing profile"""
    
    class CustomProfile(TypingProfile):
        def __init__(self, custom_name: str, custom_char: TypingCharacteristics):
            self.custom_name = custom_name
            self.custom_char = custom_char
            super().__init__()
            
        def get_characteristics(self) -> TypingCharacteristics:
            return self.custom_char
            
        def get_error_patterns(self) -> Dict[str, float]:
            return {
                'substitution': 0.4,
                'insertion': 0.2,
                'deletion': 0.2,
                'transposition': 0.2
            }
            
        def get_rhythm_patterns(self) -> Dict[str, Any]:
            return {
                'custom_profile': True
            }
    
    return CustomProfile(name, characteristics)