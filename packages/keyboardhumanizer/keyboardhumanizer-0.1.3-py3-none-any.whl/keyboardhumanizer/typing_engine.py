"""
Core Typing Engine - Realistic Human Typing Simulation
Handles the actual keystroke generation with human-like patterns
"""

import time
import random
import re
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("Warning: pynput not available. Limited keyboard functionality.")


class TypingSpeed(Enum):
    """Typing speed categories"""
    VERY_SLOW = "very_slow"      # 10-20 WPM
    SLOW = "slow"                # 20-35 WPM  
    AVERAGE = "average"          # 35-50 WPM
    FAST = "fast"               # 50-70 WPM
    VERY_FAST = "very_fast"     # 70+ WPM


class ErrorType(Enum):
    """Types of typing errors"""
    SUBSTITUTION = "substitution"    # Wrong character
    INSERTION = "insertion"          # Extra character
    DELETION = "deletion"            # Missing character
    TRANSPOSITION = "transposition"  # Swapped characters


@dataclass
class TypingStats:
    """Typing session statistics"""
    characters_typed: int = 0
    words_typed: int = 0
    errors_made: int = 0
    corrections_made: int = 0
    session_duration: float = 0.0
    current_wpm: float = 0.0
    accuracy: float = 100.0


class TypingEngine:
    """Core engine for realistic human typing simulation"""
    
    def __init__(self):
        self.controller = None
        self.setup_keyboard()
        
        # Typing characteristics
        self.base_wpm = 45  # Words per minute
        self.wpm_variance = 15  # Speed variance
        
        # Error rates (per character)
        self.error_rate = 0.02  # 2% error rate
        self.correction_rate = 0.8  # 80% of errors get corrected
        
        # Timing patterns
        self.burst_typing = True  # Type in bursts vs constant speed
        self.thinking_pauses = True  # Pause for "thinking"
        
        # Session tracking
        self.stats = TypingStats()
        self.session_start = time.time()
        self.fatigue_level = 0.0
        
        # Recent typing history for pattern analysis
        self.recent_chars = []
        self.recent_timings = []
        
    def setup_keyboard(self):
        """Setup keyboard controller"""
        if PYNPUT_AVAILABLE:
            try:
                self.controller = keyboard.Controller()
            except Exception as e:
                print(f"Warning: Could not setup keyboard controller: {e}")
        else:
            print("Warning: pynput not available. Keyboard functionality disabled.")
    
    def calculate_char_delay(self, char: str, prev_char: Optional[str] = None) -> float:
        """Calculate realistic delay between characters"""
        # Base delay from WPM (assuming 5 chars per word)
        base_delay = 60 / (self.base_wpm * 5)
        
        # Add variance
        variance = random.uniform(-0.3, 0.3) * base_delay
        delay = base_delay + variance
        
        # Adjust for character difficulty
        delay *= self._get_char_difficulty_multiplier(char, prev_char)
        
        # Adjust for fatigue
        delay *= (1 + self.fatigue_level * 0.5)
        
        # Ensure minimum delay
        return max(0.02, delay)
    
    def _get_char_difficulty_multiplier(self, char: str, prev_char: Optional[str] = None) -> float:
        """Get typing difficulty multiplier for character combinations"""
        multiplier = 1.0
        
        # Special characters are slower
        if char.isupper():
            multiplier *= 1.3  # Shift key coordination
        elif char in '!@#$%^&*()_+{}|:"<>?':
            multiplier *= 1.8  # Special symbols
        elif char in '1234567890-=[]\\;\',./':
            multiplier *= 1.2  # Numbers and punctuation
        
        # Difficult key combinations
        if prev_char and char:
            # Same finger awkward combinations
            awkward_combos = {
                ('q', 'w'), ('w', 'q'), ('e', 'r'), ('r', 'e'),
                ('t', 'y'), ('y', 't'), ('u', 'i'), ('i', 'u'),
                ('o', 'p'), ('p', 'o'), ('a', 's'), ('s', 'a'),
                ('d', 'f'), ('f', 'd'), ('g', 'h'), ('h', 'g'),
                ('j', 'k'), ('k', 'j'), ('l', ';'), (';', 'l'),
                ('z', 'x'), ('x', 'z'), ('c', 'v'), ('v', 'c'),
                ('b', 'n'), ('n', 'b'), ('m', ','), (',', 'm')
            }
            
            combo = (prev_char.lower(), char.lower())
            if combo in awkward_combos:
                multiplier *= 1.4
        
        return multiplier
    
    def should_make_error(self, char: str) -> bool:
        """Determine if an error should be made on this character"""
        error_chance = self.error_rate
        
        # Increase error rate with fatigue
        error_chance *= (1 + self.fatigue_level * 2)
        
        # Some characters more error-prone
        if char.isupper() or char in '!@#$%^&*()_+{}|:"<>?':
            error_chance *= 1.5
            
        return random.random() < error_chance
    
    def generate_error(self, intended_char: str) -> str:
        """Generate a realistic typing error"""
        error_type = random.choice(list(ErrorType))
        
        if error_type == ErrorType.SUBSTITUTION:
            return self._get_adjacent_key(intended_char)
        elif error_type == ErrorType.INSERTION:
            return intended_char + self._get_random_char()
        elif error_type == ErrorType.DELETION:
            return ""  # Character gets skipped
        else:  # TRANSPOSITION
            if len(self.recent_chars) > 0:
                # Swap current with previous
                return self.recent_chars[-1] + intended_char
            else:
                return self._get_adjacent_key(intended_char)
    
    def _get_adjacent_key(self, char: str) -> str:
        """Get a character from an adjacent keyboard key"""
        # QWERTY keyboard layout mapping
        adjacent_keys = {
            'a': 'sqwz', 'b': 'vghn', 'c': 'xdfv', 'd': 'serfxc', 'e': 'wsdr',
            'f': 'drtgvc', 'g': 'ftyhbv', 'h': 'gyujnb', 'i': 'ujko', 'j': 'huikmn',
            'k': 'jiolm', 'l': 'kop', 'm': 'njk', 'n': 'bhjm', 'o': 'iklp',
            'p': 'ol', 'q': 'wa', 'r': 'edft', 's': 'awedxz', 't': 'erfgy',
            'u': 'yhji', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc', 'y': 'tghu',
            'z': 'asx'
        }
        
        char_lower = char.lower()
        if char_lower in adjacent_keys:
            adjacent = random.choice(adjacent_keys[char_lower])
            return adjacent.upper() if char.isupper() else adjacent
        else:
            return char  # Return original if no adjacent keys defined
    
    def _get_random_char(self) -> str:
        """Get a random character for insertion errors"""
        chars = 'abcdefghijklmnopqrstuvwxyz'
        return random.choice(chars)
    
    def should_correct_error(self) -> bool:
        """Determine if the last error should be corrected"""
        return random.random() < self.correction_rate
    
    def add_thinking_pause(self) -> float:
        """Add a realistic thinking pause"""
        if not self.thinking_pauses:
            return 0.0
            
        # Thinking pauses more likely at:
        # - End of words
        # - After punctuation
        # - Beginning of sentences
        # - When fatigued
        
        pause_chance = 0.1 + (self.fatigue_level * 0.2)
        
        if random.random() < pause_chance:
            # Different types of pauses
            pause_types = [
                (0.2, 0.8),   # Quick pause
                (0.8, 2.0),   # Medium pause  
                (2.0, 5.0),   # Long thinking pause
            ]
            
            weights = [0.6, 0.3, 0.1]  # Favor shorter pauses
            pause_range = random.choices(pause_types, weights=weights)[0]
            return random.uniform(*pause_range)
        
        return 0.0
    
    def type_character(self, char: str) -> bool:
        """Type a single character with human-like behavior"""
        if not self.controller:
            print(f"Would type: '{char}'")
            return True
            
        try:
            # Add pre-character delay
            prev_char = self.recent_chars[-1] if self.recent_chars else None
            delay = self.calculate_char_delay(char, prev_char)
            time.sleep(delay)
            
            # Check for errors
            if self.should_make_error(char):
                error_char = self.generate_error(char)
                
                if error_char:  # Not a deletion error
                    if len(error_char) > 1:  # Transposition or insertion
                        for c in error_char:
                            self.controller.type(c)
                            self.stats.characters_typed += 1
                    else:  # Substitution
                        self.controller.type(error_char)
                        self.stats.characters_typed += 1
                    
                    self.stats.errors_made += 1
                    
                    # Decide whether to correct
                    if self.should_correct_error():
                        time.sleep(random.uniform(0.1, 0.5))  # Pause before correction
                        
                        # Backspace to remove error
                        backspaces = len(error_char) if len(error_char) > 1 else 1
                        for _ in range(backspaces):
                            self.controller.press(Key.backspace)
                            self.controller.release(Key.backspace)
                            time.sleep(random.uniform(0.05, 0.15))
                        
                        # Type correct character
                        self.controller.type(char)
                        self.stats.corrections_made += 1
                        self.stats.characters_typed += 1
                else:
                    # Deletion error - character gets skipped initially
                    # May be noticed and corrected later
                    if self.should_correct_error():
                        time.sleep(random.uniform(0.2, 0.8))  # Longer pause to "notice"
                        self.controller.type(char)
                        self.stats.corrections_made += 1
                        self.stats.characters_typed += 1
            else:
                # Type character normally
                self.controller.type(char)
                self.stats.characters_typed += 1
            
            # Update tracking
            self.recent_chars.append(char)
            if len(self.recent_chars) > 10:
                self.recent_chars.pop(0)
                
            self.recent_timings.append(time.time())
            if len(self.recent_timings) > 50:
                self.recent_timings.pop(0)
            
            return True
            
        except Exception as e:
            print(f"Error typing character '{char}': {e}")
            return False
    
    def type_word(self, word: str) -> bool:
        """Type a complete word with human-like patterns"""
        if not word:
            return True
            
        # Add pre-word thinking pause
        thinking_pause = self.add_thinking_pause()
        if thinking_pause > 0:
            time.sleep(thinking_pause)
        
        # Type each character
        for i, char in enumerate(word):
            if not self.type_character(char):
                return False
                
            # Update fatigue slightly
            self.fatigue_level = min(0.5, self.fatigue_level + 0.001)
        
        self.stats.words_typed += 1
        return True
    
    def type_text(self, text: str, use_copy_paste: bool = True) -> bool:
        """Type complete text with realistic human behavior"""
        words = text.split()
        total_words = len(words)
        
        for i, word in enumerate(words):
            # Occasionally use copy-paste for repeated text
            if use_copy_paste and self._should_copy_paste(word, i, words):
                if self._perform_copy_paste(word):
                    continue
            
            # Type the word normally
            if not self.type_word(word):
                return False
            
            # Add space after word (except last word)
            if i < total_words - 1:
                if not self.type_character(' '):
                    return False
        
        return True
    
    def _should_copy_paste(self, word: str, index: int, all_words: List[str]) -> bool:
        """Determine if word should be copy-pasted instead of typed"""
        # Only for longer words/phrases
        if len(word) < 6:
            return False
            
        # Check if this word appeared recently
        recent_words = all_words[max(0, index - 10):index]
        if word in recent_words:
            return random.random() < 0.3  # 30% chance to copy-paste repeated words
            
        # Check for common copy-paste candidates
        copy_paste_candidates = [
            'email', 'password', 'username', 'address', 'phone',
            'http', 'https', 'www', '.com', '.org', '.net'
        ]
        
        if any(candidate in word.lower() for candidate in copy_paste_candidates):
            return random.random() < 0.4  # 40% chance
            
        return False
    
    def _perform_copy_paste(self, text: str) -> bool:
        """Simulate copy-paste behavior"""
        if not self.controller:
            print(f"Would copy-paste: '{text}'")
            return True
            
        try:
            # Simulate typing the text quickly (as if pasted)
            # Add slight delay to simulate paste action
            time.sleep(random.uniform(0.1, 0.3))
            
            # Type text quickly (simulate paste)
            for char in text:
                self.controller.type(char)
                time.sleep(random.uniform(0.01, 0.03))  # Very fast typing
                
            self.stats.characters_typed += len(text)
            return True
            
        except Exception as e:
            print(f"Error during copy-paste simulation: {e}")
            return False
    
    def add_spontaneous_correction(self, text_so_far: str) -> bool:
        """Add spontaneous corrections (going back to fix earlier errors)"""
        if len(text_so_far) < 10 or not self.controller:
            return False
            
        # 5% chance of spontaneous correction
        if random.random() > 0.05:
            return False
            
        try:
            # Go back 2-8 characters
            backtrack_distance = random.randint(2, min(8, len(text_so_far)))
            
            # Pause to "notice" error
            time.sleep(random.uniform(0.3, 1.0))
            
            # Backspace
            for _ in range(backtrack_distance):
                self.controller.press(Key.backspace)
                self.controller.release(Key.backspace)
                time.sleep(random.uniform(0.08, 0.15))
            
            # Retype the section (possibly with improvements)
            section_to_retype = text_so_far[-backtrack_distance:]
            for char in section_to_retype:
                self.type_character(char)
                
            return True
            
        except Exception as e:
            print(f"Error during spontaneous correction: {e}")
            return False
    
    def update_fatigue(self, session_duration: float):
        """Update fatigue level based on session duration"""
        # Fatigue increases over time, affecting speed and accuracy
        hours_typed = session_duration / 3600
        self.fatigue_level = min(0.8, hours_typed * 0.1)  # 10% fatigue per hour, max 80%
    
    def get_current_wpm(self) -> float:
        """Calculate current words per minute"""
        if len(self.recent_timings) < 2:
            return 0.0
            
        time_span = self.recent_timings[-1] - self.recent_timings[0]
        if time_span <= 0:
            return 0.0
            
        chars_typed = len(self.recent_timings)
        words_typed = chars_typed / 5  # Standard: 5 characters per word
        minutes = time_span / 60
        
        return words_typed / minutes if minutes > 0 else 0.0
    
    def get_session_stats(self) -> TypingStats:
        """Get current session statistics"""
        self.stats.session_duration = time.time() - self.session_start
        self.stats.current_wpm = self.get_current_wpm()
        
        if self.stats.characters_typed > 0:
            accuracy = ((self.stats.characters_typed - self.stats.errors_made) / 
                       self.stats.characters_typed) * 100
            self.stats.accuracy = max(0, accuracy)
        
        return self.stats