# Keyboard Humanizer

**Human-like keyboard automation for Python.**  
Simulates realistic typing, errors, corrections, and even the occasional uncorrected typo—just like a real human.

---

## 🚀 Installation

```bash
pip install keyboardhumanizer
```

- Requires Python 3.7+
- Depends on [pyautogui](https://pyautogui.readthedocs.io/) (auto-installed)
- Works on **Windows, Linux, and macOS** (auto-detects your OS)

---

## ⚡ Quick Start

```python
from keyboardhumanizer import KeyboardHumanizer

humanizer = KeyboardHumanizer()
humanizer.type_text("Hello, this is a human-like typing demo!")
```

---

## 🎬 Demo

Run the advanced demo for a full interactive experience:

```bash
python demo_advanced.py
```

- **Basic Demo**: Automated showcase of human typing.
- **Interactive Demo**: Try custom text, switch profiles, tweak settings, view stats, and more.

---

## 🧑‍💻 Typing Profiles

Choose from multiple built-in profiles:

```python
profiles = humanizer.get_available_profiles()
print(profiles)  # ['casual', 'professional', 'beginner', 'gamer', ...]
humanizer.set_profile_by_name('professional')
```

---

## ⚙️ Settings & Configuration

You can customize the humanizer's behavior at runtime:

```python
# View current config
print(humanizer.get_current_config())

# Change settings
humanizer.configure(
    simulate_errors=True,
    use_copy_paste=False,
    add_thinking_pauses=True,
    simulate_fatigue=True,
    context_aware=True,
    learning_mode=False
)
```

**Available settings:**
- `simulate_errors` (bool): Make realistic typing mistakes.
- `use_copy_paste` (bool): Use copy-paste for emails, code, etc.
- `add_thinking_pauses` (bool): Add natural pauses between sentences.
- `simulate_fatigue` (bool): Typing slows down over time.
- `context_aware` (bool): Adjusts behavior for code, emails, etc.
- `learning_mode` (bool): Adapts to your typing over time.

---

## 🛠️ API Reference

- `type_text(text: str, **kwargs)`: Type text with human-like behavior.
- `set_profile_by_name(profile_name: str)`: Switch typing profile.
- `get_available_profiles()`: List all profiles.
- `configure(**kwargs)`: Change settings.
- `print_stats()`: Print session statistics.
- `reset_session()`: Reset stats and fatigue.

---

## 💡 Use Cases

- UI/UX testing for anti-bot detection
- Automated data entry that looks human
- Demos and screencasts
- Accessibility research
- QA for input fields

---

## 🖥️ Platform Support

- **Windows, Linux, macOS**: Auto-detected, no config needed.
- If a feature isn't supported, you'll get a clear error.
- Requires GUI access (not headless).

---

## ❓ Troubleshooting

- **pyautogui not working?**  
  Make sure you have a GUI session and the right permissions.
- **Not typing in the right window?**  
  Focus the target window before running the demo.

---

## 🤝 Contributing

PRs and issues welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

MIT

## 🧪 Advanced Testing

To run the full coverage advanced keyboard test (exercises all behaviors, profiles, mistakes, corrections, and hotkeys):

```bash
python tests/test_keyboard_advanced.py
```

This will type, press keys, use hotkeys, and demonstrate all advanced behaviors for robust testing.
