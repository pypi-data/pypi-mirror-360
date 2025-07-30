import random
import time
from pynput.mouse import Controller as MouseController, Button
import math

# Helper functions for human-like movement (bezier, jitter, etc.)
def bezier_curve(start, end, steps=50, intensity=1.0):
    x0, y0 = start
    x2, y2 = end
    mx, my = (x0 + x2) / 2, (y0 + y2) / 2
    offset = random.uniform(-100, 100) * intensity
    dx, dy = x2 - x0, y2 - y0
    length = math.hypot(dx, dy)
    if length == 0:
        return [start, end]
    perp_x, perp_y = -dy / length, dx / length
    cx, cy = mx + perp_x * offset, my + perp_y * offset
    points = []
    for t in [i / steps for i in range(steps + 1)]:
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x2
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y2
        # Add micro-jitter
        x += random.uniform(-1, 1)
        y += random.uniform(-1, 1)
        points.append((int(x), int(y)))
    return points

class HumanMouseController:
    def __init__(self, screen_width=None, screen_height=None, tolerance=8):
        if screen_width is None or screen_height is None:
            raise ValueError("screen_width and screen_height must be provided for HumanMouseController")
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tolerance = tolerance
        self.mouse = MouseController()

    def move(self, pos):
        # 5% chance to overshoot and correct
        if random.random() < 0.05:
            print("[Quirk] Overshoot and correct")
            overshoot = (
                min(self.screen_width-1, pos[0]+random.randint(20, 60)),
                min(self.screen_height-1, pos[1]+random.randint(20, 60))
            )
            self._move_human_like(overshoot)
            self._move_human_like(pos)
        else:
            self._move_human_like(pos)
        # Correction logic: if not close enough, correct
        actual = self.mouse.position
        if math.hypot(actual[0]-pos[0], actual[1]-pos[1]) > self.tolerance:
            print(f"[Correction] Landed at {actual}, correcting to {pos}")
            self._move_human_like(pos)
        # 10% chance to fidget after move
        if random.random() < 0.10:
            print("[Quirk] Fidget after move")
            self._fidget(pos)

    def click(self, pos, button=Button.left):
        self.move(pos)
        self.mouse.click(button)
        # 2% chance to rage click
        if random.random() < 0.02:
            print("[Quirk] Rage click")
            for _ in range(random.randint(3, 7)):
                self.mouse.click(button)
                time.sleep(random.uniform(0.03, 0.09))
        # 3% chance to double click
        elif random.random() < 0.03:
            print("[Quirk] Double click")
            self.mouse.click(button)

    def hover(self, pos):
        # 5% chance to ADHD wander before hover
        if random.random() < 0.05:
            print("[Quirk] ADHD wander before hover")
            self._adhd_wander()
            self.move(pos)
        else:
            self.move(pos)

    def scroll(self, amount):
        self.mouse.scroll(0, amount)

    def _move_human_like(self, pos):
        start = self.mouse.position
        points = bezier_curve(start, pos, steps=random.randint(30, 60), intensity=random.uniform(0.5, 1.2))
        for p in points:
            self.mouse.position = p
            time.sleep(random.uniform(0.002, 0.008))
        # Simulate a small pause at the end
        time.sleep(random.uniform(0.03, 0.09))

    def _fidget(self, pos):
        # Randomly choose between micro and macro fidgeting
        if random.random() < 0.5:
            print("[Quirk] Micro fidget")
            for _ in range(random.randint(3, 7)):
                # Small, tight jitter
                jitter = (
                    pos[0] + random.randint(-10, 10),
                    pos[1] + random.randint(-10, 10)
                )
                self._move_human_like(jitter)
                self._move_human_like(pos)
        else:
            print("[Quirk] Macro fidget")
            for _ in range(random.randint(2, 4)):
                # Large, spread-out jitter
                jitter = (
                    pos[0] + random.randint(-60, 60),
                    pos[1] + random.randint(-60, 60)
                )
                self._move_human_like(jitter)
                self._move_human_like(pos)

    def _adhd_wander(self):
        start = self.mouse.position
        wander_time = random.uniform(1.2, 3.5)
        t0 = time.time()
        while time.time() - t0 < wander_time:
            # Much larger, more erratic jumps
            wander = (
                min(self.screen_width-1, max(0, start[0]+random.randint(-250, 250))),
                min(self.screen_height-1, max(0, start[1]+random.randint(-250, 250)))
            )
            self._move_human_like(wander)
            time.sleep(random.uniform(0.02, 0.09))
        # Return to start
        self._move_human_like(start) 