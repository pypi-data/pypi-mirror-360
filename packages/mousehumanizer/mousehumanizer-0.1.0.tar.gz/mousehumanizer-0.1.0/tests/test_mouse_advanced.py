import random
import time
from humanmouse import HumanMouse

# Robust cross-platform screen size detection (as before)
screen_width = screen_height = None
try:
    from AppKit import NSScreen
    frame = NSScreen.mainScreen().frame()
    screen_width, screen_height = int(frame.size.width), int(frame.size.height)
except Exception:
    try:
        import ctypes
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
    except Exception:
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
        except Exception:
            pass

if screen_width is None or screen_height is None:
    print("[Test] Could not auto-detect screen size. Please enter manually.")
    try:
        screen_width = int(input("Enter screen width: "))
        screen_height = int(input("Enter screen height: "))
    except Exception:
        raise RuntimeError("Unable to determine screen size. Please provide screen_width and screen_height.")

mouse = HumanMouse(screen_width=screen_width, screen_height=screen_height)

def random_point():
    return (random.randint(0, screen_width-1), random.randint(0, screen_height-1))

print("[Test] Starting full coverage mouse behavior test...")

# 1. Public API: many iterations to probabilistically trigger quirks
for i in range(30):
    action = random.choice(['move', 'click', 'hover', 'scroll'])
    pos = random_point()
    if action == 'move':
        print(f"[Test] move to {pos}")
        try:
            mouse.move(pos, duration=random.uniform(0.2, 1.5))
        except TypeError:
            mouse.move(pos)
    elif action == 'click':
        print(f"[Test] click at {pos}")
        mouse.click(pos)
    elif action == 'hover':
        print(f"[Test] hover at {pos}")
        mouse.hover(pos)
    elif action == 'scroll':
        amount = random.choice([-10, -5, 5, 10])
        print(f"[Test] scroll {amount}")
        try:
            mouse.scroll(amount)
        except AttributeError:
            print("[Test] Scroll not implemented on this platform.")
    time.sleep(random.uniform(0.2, 0.7))

# 2. Directly test private methods for guaranteed coverage
print("[Test] Forcing ADHD wander...")
mouse._adhd_wander()
print("[Test] Forcing fidget...")
mouse._fidget(random_point())

print("[Test] Full coverage mouse behavior test complete!") 