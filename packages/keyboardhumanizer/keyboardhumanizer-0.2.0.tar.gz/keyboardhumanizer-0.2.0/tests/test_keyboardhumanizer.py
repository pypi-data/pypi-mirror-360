import pytest
from keyboardhumanizer import type_text, press_key, hotkey

def test_type_text():
    # This will type 'Hello, world!' wherever the cursor is focused
    type_text('Hello, world!')

def test_press_key():
    press_key('enter')

def test_hotkey():
    hotkey('ctrl', 'a')
    # No assertion: just check for errors 