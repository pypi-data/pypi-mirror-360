"""
Main Keyboard Humanizer Class
Combines typing engine with profiles for complete human typing simulation
"""

import time
import random
from typing import Optional, Dict, Any, List
from .typing_engine import TypingEngine, TypingStats
from .typing_profiles import (
    TypingProfile, get_profile, list_available_profiles, 
    get_random_profile, get_profile_by_name, ProfessionalProfile, CasualProfile
)


class KeyboardHumanizer:
    """Main class for human-like keyboard typing simulation"""
    
    def __init__(self, profile: Optional[TypingProfile] = None):
        """
        Initialize the Keyboard Humanizer
        
        Args:
            profile: Typing profile to use. If None, uses CasualProfile
        """
        self.engine = TypingEngine()
        self.profile = profile or CasualProfile()
        self.apply_profile()
        
        # Configuration
        self.simulate_errors = True
        self.auto_correct = True
        self.use_copy_paste = True
        self.add_thinking_pauses = True
        self.simulate_fatigue = True
        
        # Advanced features
        self.context_aware = True  # Adjust behavior based on text content
        self.learning_mode = False  # Learn from typing patterns
        
        print(f"Keyboard Humanizer initialized with {self.profile.name} profile")
    
    def apply_profile(self):
        """Apply the current profile to the typing engine"""
        if self.profile:
            self.profile.apply_to_engine(self.engine)
    
    def set_profile(self, profile: TypingProfile):
        """Change the typing profile"""
        self.profile = profile
        self.apply_profile()
        print(f"Profile changed to {self.profile.name}")
    
    def set_profile_by_name(self, profile_name: str) -> bool:
        """Set profile by name"""
        profile = get_profile(profile_name)
        if profile:
            self.set_profile(profile)
            return True
        else:
            print(f"Profile '{profile_name}' not found")
            return False
    
    def type_text(self, text: str, **kwargs) -> bool:
        """
        Type text with human-like behavior
        
        Args:
            text: Text to type
            **kwargs: Additional options
                - simulate_errors: Override error simulation
                - use_copy_paste: Override copy-paste behavior
                - add_pauses: Override thinking pauses
                - speed_multiplier: Speed adjustment (1.0 = normal)
        
        Returns:
            bool: True if successful, False if error
        """
        # Apply temporary settings
        original_settings = self._backup_settings()
        self._apply_temp_settings(kwargs)
        
        try:
            # Pre-typing setup
            self._prepare_for_typing(text)
            
            # Context analysis
            if self.context_aware:
                self._analyze_text_context(text)
            
            # Main typing process
            success = self._type_text_with_behavior(text)
            
            # Post-typing cleanup
            self._finalize_typing()
            
            return success
            
        finally:
            # Restore original settings
            self._restore_settings(original_settings)
    
    def _backup_settings(self) -> Dict[str, Any]:
        """Backup current settings"""
        return {
            'simulate_errors': self.simulate_errors,
            'auto_correct': self.auto_correct,
            'use_copy_paste': self.use_copy_paste,
            'add_thinking_pauses': self.add_thinking_pauses
        }
    
    def _restore_settings(self, settings: Dict[str, Any]):
        """Restore settings"""
        for key, value in settings.items():
            setattr(self, key, value)
    
    def _apply_temp_settings(self, kwargs: Dict[str, Any]):
        """Apply temporary settings from kwargs"""
        if 'simulate_errors' in kwargs:
            self.simulate_errors = kwargs['simulate_errors']
        if 'use_copy_paste' in kwargs:
            self.use_copy_paste = kwargs['use_copy_paste']
        if 'add_pauses' in kwargs:
            self.add_thinking_pauses = kwargs['add_pauses']
        if 'speed_multiplier' in kwargs:
            self.engine.base_wpm = int(self.engine.base_wpm * kwargs['speed_multiplier'])
    
    def _prepare_for_typing(self, text: str):
        """Prepare for typing session"""
        if self.simulate_fatigue:
            session_duration = time.time() - self.engine.session_start
            self.engine.update_fatigue(session_duration)
    
    def _analyze_text_context(self, text: str):
        """Analyze text context and adjust behavior"""
        # Detect text type and adjust accordingly
        if self._is_code_text(text):
            self._adjust_for_code()
        elif self._is_email_text(text):
            self._adjust_for_email()
        elif self._is_formal_text(text):
            self._adjust_for_formal()
        elif self._has_repetitive_content(text):
            self._adjust_for_repetitive()
    
    def _is_code_text(self, text: str) -> bool:
        """Detect if text is code"""
        code_indicators = [
            'def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ',
            '{', '}', '[', ']', '()', '=>', '==', '!=', '&&', '||',
            'function', 'const', 'let', 'var', 'return'
        ]
        return any(indicator in text for indicator in code_indicators)
    
    def _is_email_text(self, text: str) -> bool:
        """Detect if text is email"""
        email_indicators = [
            '@', 'Dear', 'Sincerely', 'Best regards', 'Hi ', 'Hello',
            'Subject:', 'From:', 'To:', '.com', '.org', '.net'
        ]
        return any(indicator in text for indicator in email_indicators)
    
    def _is_formal_text(self, text: str) -> bool:
        """Detect if text is formal writing"""
        formal_indicators = [
            'furthermore', 'therefore', 'consequently', 'moreover',
            'however', 'nevertheless', 'accordingly', 'thus'
        ]
        return any(indicator in text.lower() for indicator in formal_indicators)
    
    def _has_repetitive_content(self, text: str) -> bool:
        """Detect repetitive content"""
        words = text.split()
        unique_words = set(words)
        return len(unique_words) / len(words) < 0.7  # Less than 70% unique words
    
    def _adjust_for_code(self):
        """Adjust typing behavior for code"""
        # Slower, more careful with symbols
        self.engine.base_wpm = int(self.engine.base_wpm * 0.8)
        self.engine.error_rate *= 0.7  # Fewer errors
        self.engine.thinking_pauses = True
        self.use_copy_paste = True  # Common in coding
        
    def _adjust_for_email(self):
        """Adjust typing behavior for email"""
        # Normal speed, careful with addresses
        self.engine.thinking_pauses = True
        self.use_copy_paste = True  # For email addresses
        
    def _adjust_for_formal(self):
        """Adjust typing behavior for formal text"""
        # More careful, fewer errors
        self.engine.base_wpm = int(self.engine.base_wpm * 0.9)
        self.engine.error_rate *= 0.8
        self.engine.thinking_pauses = True
        
    def _adjust_for_repetitive(self):
        """Adjust typing behavior for repetitive text"""
        # Faster, more copy-paste
        self.engine.base_wpm = int(self.engine.base_wpm * 1.2)
        self.use_copy_paste = True
    
    def _type_text_with_behavior(self, text: str) -> bool:
        """Type text with full behavioral simulation"""
        # Split into sentences for natural pacing
        sentences = self._split_into_sentences(text)
        
        for i, sentence in enumerate(sentences):
            # Add thinking pause between sentences
            if i > 0 and self.add_thinking_pauses:
                pause = self.engine.add_thinking_pause()
                if pause > 0:
                    time.sleep(pause)
            
            # Type the sentence
            if not self._type_sentence(sentence):
                return False
            
            # Occasionally add spontaneous corrections
            if random.random() < 0.1:  # 10% chance
                self.engine.add_spontaneous_correction(sentence)
        
        return True
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for natural pacing"""
        # Simple sentence splitting
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in '.!?':
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        # Add remaining text
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        return sentences
    
    def _type_sentence(self, sentence: str) -> bool:
        """Type a single sentence"""
        # Add a small chance to make a spelling mistake and NOT fix it
        if len(sentence) > 5 and random.random() < 0.015:  # 1.5% chance
            idx = random.randint(1, len(sentence) - 2)
            wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
            if sentence[idx] != wrong_char:
                sentence = sentence[:idx] + wrong_char + sentence[idx+1:]
                # Do NOT correct it, just type as is
        return self.engine.type_text(sentence, use_copy_paste=self.use_copy_paste)
    
    def _finalize_typing(self):
        """Clean up after typing"""
        # Update learning if enabled
        if self.learning_mode:
            self._update_learning_patterns()
    
    def _update_learning_patterns(self):
        """Update learning patterns based on session"""
        # Placeholder for learning implementation
        stats = self.get_session_stats()
        if stats.accuracy < 95:
            # Reduce speed if accuracy is low
            self.engine.base_wpm = int(self.engine.base_wpm * 0.95)
        elif stats.accuracy > 98:
            # Increase speed if accuracy is high
            self.engine.base_wpm = int(self.engine.base_wpm * 1.02)
    
    def get_session_stats(self) -> TypingStats:
        """Get current session statistics"""
        return self.engine.get_session_stats()
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available typing profiles"""
        return list_available_profiles()
    
    def reset_session(self):
        """Reset the typing session"""
        self.engine.stats = TypingStats()
        self.engine.session_start = time.time()
        self.engine.fatigue_level = 0.0
        self.engine.recent_chars = []
        self.engine.recent_timings = []
        print("Session reset")
    
    def configure(self, **kwargs):
        """Configure humanizer settings"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                print(f"Set {key} = {value}")
            else:
                print(f"Unknown setting: {key}")
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return {
            'profile': self.profile.name,
            'simulate_errors': self.simulate_errors,
            'auto_correct': self.auto_correct,
            'use_copy_paste': self.use_copy_paste,
            'add_thinking_pauses': self.add_thinking_pauses,
            'simulate_fatigue': self.simulate_fatigue,
            'context_aware': self.context_aware,
            'learning_mode': self.learning_mode
        }
    
    def print_stats(self):
        """Print current session statistics"""
        stats = self.get_session_stats()
        config = self.get_current_config()
        
        print("\n=== Keyboard Humanizer Session Stats ===")
        print(f"Profile: {config['profile']}")
        print(f"Characters typed: {stats.characters_typed}")
        print(f"Words typed: {stats.words_typed}")
        print(f"Current WPM: {stats.current_wpm:.1f}")
        print(f"Accuracy: {stats.accuracy:.1f}%")
        print(f"Errors made: {stats.errors_made}")
        print(f"Corrections made: {stats.corrections_made}")
        print(f"Session duration: {stats.session_duration:.1f}s")
        print(f"Fatigue level: {self.engine.fatigue_level:.1%}")
        print("=" * 40)
    
    def demo_mode(self, duration: int = 60):
        """Run in demo mode for specified duration"""
        print(f"Starting demo mode for {duration} seconds...")
        
        demo_texts = [
            "Hello, this is a demonstration of human-like typing.",
            "Notice how the speed varies naturally, just like real typing.",
            "Sometimes there are small mistakes that get corrected.",
            "The system adapts to different types of content automatically.",
            "Programming code is typed more carefully: def hello_world():",
            "Email addresses like user@example.com are often copy-pasted.",
            "This creates a very realistic typing simulation!"
        ]
        
        start_time = time.time()
        text_index = 0
        
        while time.time() - start_time < duration:
            text = demo_texts[text_index % len(demo_texts)]
            print(f"\nTyping: {text}")
            
            self.type_text(text)
            
            # Add break between texts
            time.sleep(random.uniform(2, 5))
            text_index += 1
        
        print(f"\nDemo completed!")
        self.print_stats()


# Convenience function
def create_humanizer(profile_name: str = "casual") -> KeyboardHumanizer:
    """Create a keyboard humanizer with specified profile"""
    profile = get_profile(profile_name)
    return KeyboardHumanizer(profile)