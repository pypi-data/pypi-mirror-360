# Mouse Humanizer

**Human-like mouse automation for Python.**  
Simulates realistic, non-robotic mouse movement, clicks, hovers, scrolling, and more—with quirks, fidgets, and overshoots for true human flavor.

---

## 🚀 Installation

```bash
pip install mousehumanizer
```

- Requires Python 3.7+
- Depends on [pynput](https://pynput.readthedocs.io/) (auto-installed)
- Works on **Windows** and **Linux** (macOS support: see below)

---

## ⚡ Quick Start

```python
from humanmouse import HumanMouse

mouse = HumanMouse()
center = (mouse.screen_width // 2, mouse.screen_height // 2)
mouse.move(center, duration=0.5)
mouse.click(center)
mouse.scroll(5)
mouse.hover((100, 100))
```

---

## 🎬 Demo & Testing

Run the test/demo to see human-like mouse actions in action:

```bash
pytest tests/test_humanmouse.py
```

- Moves the mouse, clicks, scrolls, and hovers using the humanized logic.
- Prints backend/OS info for debugging.

---

## 🧪 Advanced Testing

To run the full coverage advanced mouse test (exercises all behaviors, including ADHD wander, fidget, overshoot, rage click, etc.):

```bash
python tests/test_mouse_advanced.py
```

This will move, click, hover, scroll, and directly trigger all advanced behaviors for robust testing.

---

## 🛠️ API Reference

### `HumanMouse`
- `move(pos: tuple, duration=0.5)`: Move mouse to position with human-like path.
- `click(pos: tuple, button='left')`: Move and click at position (with quirks).
- `hover(pos: tuple)`: Move and hover (sometimes with ADHD wander).
- `scroll(amount: int)`: Scroll up/down (stub on some platforms).
- `screen_width`, `screen_height`: Properties for screen size.

### Top-level (planned):
- `type_text(text: str)`: (stub)
- `press_key(key: str)`: (stub)
- `hotkey(*args)`: (stub)

---

## 💡 Use Cases

- UI/UX testing for anti-bot detection
- Automated mouse actions that look human
- Demos and screencasts
- Accessibility research
- QA for mouse-driven interfaces

---

## 🖥️ Platform Support

- **Windows:** Uses `pynput` for mouse control.
- **Linux:** Uses custom `SystemCursor` logic.
- **macOS:** Not officially supported yet (PRs welcome!).
- The package auto-selects the backend based on your OS.
- If a feature isn't supported, you'll get a clear error or stub.

---

## ❓ Troubleshooting

- **pynput not working?**  
  Make sure you have a GUI session and the right permissions.
- **Not moving/clicking in the right place?**  
  Focus the target window before running the demo/test.
- **macOS:** You may need to grant accessibility permissions for automation.

---

## 🤝 Contributing

PRs and issues welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

MIT 