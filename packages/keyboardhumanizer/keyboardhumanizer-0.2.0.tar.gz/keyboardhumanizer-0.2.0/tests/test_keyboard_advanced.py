import time
from keyboardhumanizer import KeyboardHumanizer, type_text, press_key, hotkey

print("[Test] Starting advanced keyboard humanizer test...")

# Test with KeyboardHumanizer class (if available)
try:
    humanizer = KeyboardHumanizer()
    print("[Test] Typing with default profile...")
    humanizer.type_text("This is a test of human-like typing.")
    time.sleep(1)
    print("[Test] Typing with 'beginner' profile (more mistakes)...")
    humanizer.set_profile_by_name('beginner')
    humanizer.type_text("Mistakes and corrections should be visible here.")
    time.sleep(1)
    print("[Test] Typing with 'professional' profile (faster, accurate)...")
    humanizer.set_profile_by_name('professional')
    humanizer.type_text("This should be fast and accurate.")
except Exception as e:
    print(f"[Test] KeyboardHumanizer class not available: {e}")
    print("[Test] Falling back to function-based API.")
    type_text("This is a test of human-like typing (function API).\n")
    time.sleep(1)

# Test press_key and hotkey
print("[Test] Pressing Enter key...")
press_key('enter')
print("[Test] Pressing Ctrl+A hotkey...")
hotkey('ctrl', 'a')

print("[Test] Advanced keyboard humanizer test complete!") 