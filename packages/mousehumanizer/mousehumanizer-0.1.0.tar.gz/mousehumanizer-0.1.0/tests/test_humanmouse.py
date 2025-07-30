import pytest
from humanmouse import HumanMouse

def test_mouse_move_and_click():
    mouse = HumanMouse()
    # Move to a safe position (center of screen)
    screen_width, screen_height = mouse.screen_width, mouse.screen_height
    center = (screen_width // 2, screen_height // 2)
    mouse.move(center, duration=0.5)
    mouse.click(center)
    # No assertion: this is a smoke test for errors

def test_mouse_scroll():
    mouse = HumanMouse()
    mouse.scroll(5)
    mouse.scroll(-5)
    # No assertion: just check for errors

