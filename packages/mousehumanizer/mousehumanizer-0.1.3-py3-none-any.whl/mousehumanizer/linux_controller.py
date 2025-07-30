import random
import time
import math
from .system_cursor import SystemCursor

# Helper for human-like movement (bezier, jitter, etc.)
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
        x += random.uniform(-1, 1)
        y += random.uniform(-1, 1)
        points.append((int(x), int(y)))
    return points

class LinuxHumanMouseController:
    def __init__(self, screen_width=1920, screen_height=1080, tolerance=8):
        self.cursor = SystemCursor()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tolerance = tolerance

    def move(self, pos, duration=0.5):
        # duration is currently ignored, but accepted for API compatibility
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
        actual = self.cursor.get_position()
        if math.hypot(actual[0]-pos[0], actual[1]-pos[1]) > self.tolerance:
            print(f"[Correction] Landed at {actual}, correcting to {pos}")
            self._move_human_like(pos)
        if random.random() < 0.10:
            print("[Quirk] Fidget after move")
            self._fidget(pos)

    def click(self, pos, button='left'):
        self.move(pos)
        self.cursor.click_on(pos, button=button)
        # 2% chance to rage click
        if random.random() < 0.02:
            print("[Quirk] Rage click")
            for _ in range(random.randint(3, 7)):
                self.cursor.click_on(pos, button=button)
                time.sleep(random.uniform(0.03, 0.09))
        # 3% chance to double click
        elif random.random() < 0.03:
            print("[Quirk] Double click")
            self.cursor.click_on(pos, button=button)

    def hover(self, pos):
        # 5% chance to ADHD wander before hover
        if random.random() < 0.05:
            print("[Quirk] ADHD wander before hover")
            self._adhd_wander()
            self.move(pos)
        else:
            self.move(pos)

    def _move_human_like(self, pos):
        start = self.cursor.get_position()
        points = bezier_curve(start, pos, steps=random.randint(30, 60), intensity=random.uniform(0.5, 1.2))
        for p in points:
            self.cursor.move_to(p)
            time.sleep(random.uniform(0.002, 0.008))
        time.sleep(random.uniform(0.03, 0.09))

    def _fidget(self, pos):
        for _ in range(random.randint(3, 7)):
            jitter = (pos[0]+random.randint(-40, 40), pos[1]+random.randint(-40, 40))
            self._move_human_like(jitter)
            self._move_human_like(pos)

    def _adhd_wander(self):
        start = self.cursor.get_position()
        wander_time = random.uniform(1.2, 3.5)
        t0 = time.time()
        while time.time() - t0 < wander_time:
            wander = (
                min(self.screen_width-1, max(0, start[0]+random.randint(-250, 250))),
                min(self.screen_height-1, max(0, start[1]+random.randint(-250, 250)))
            )
            self._move_human_like(wander)
            time.sleep(random.uniform(0.02, 0.09))
        self._move_human_like(start)

    def scroll(self, amount):
        print(f"[Stub] Scrolling {amount}")
        pass 