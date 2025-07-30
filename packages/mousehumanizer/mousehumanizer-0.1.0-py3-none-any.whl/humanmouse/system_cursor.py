"""
System Cursor - Human-like mouse movement for Linux
Simple, natural human behavior without profiles or display management
"""

import time
import random
import math
from typing import List, Tuple, Optional

try:
    from pynput import mouse
    from pynput.mouse import Button, Listener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    from Xlib import display, X
    from Xlib.ext.xtest import fake_input
    X11_AVAILABLE = True
except ImportError:
    X11_AVAILABLE = False

from .utilities.human_curve_generator import HumanizeMouseTrajectory
from .utilities.calculate_and_randomize import calculate_and_randomize


class SystemCursor:
    """Human-like system cursor with natural behavior"""
    
    def __init__(self):
        self.controller = None
        self.x11_display = None
        self.screen_width = 1920  # Default, will be detected
        self.screen_height = 1080  # Default, will be detected
        
        # Human behavior parameters - simple and natural
        self.speed_variance = 0.3  # 30% speed variation
        self.error_chance = 0.08   # 8% chance of slight overshoot
        self.correction_chance = 0.7  # 70% chance to correct errors
        self.micro_pause_chance = 0.12  # 12% chance of small pauses
        self.fatigue_level = 0.0   # Gradual fatigue buildup
        
        # Movement history for natural patterns
        self.recent_moves = []
        self.session_start = time.time()
        
        self._setup_cursor()
        self._detect_screen_resolution()
    
    def _setup_cursor(self):
        """Setup cursor control with fallback methods"""
        # Try pynput first (most reliable)
        if PYNPUT_AVAILABLE:
            try:
                self.controller = mouse.Controller()
                return
            except Exception as e:
                print(f"Pynput setup failed: {e}")
        
        # Fallback to X11
        if X11_AVAILABLE:
            try:
                self.x11_display = display.Display()
                return
            except Exception as e:
                print(f"X11 setup failed: {e}")
        
        print("Warning: No cursor control method available")
    
    def _detect_screen_resolution(self):
        """Detect screen resolution safely"""
        try:
            if self.x11_display:
                screen = self.x11_display.screen()
                self.screen_width = screen.width_in_pixels
                self.screen_height = screen.height_in_pixels
            elif self.controller:
                # Try to get screen bounds by moving to corners
                current_pos = self.controller.position
                
                # Try moving to large coordinates to find bounds
                try:
                    self.controller.position = (9999, 9999)
                    max_pos = self.controller.position
                    self.screen_width = max_pos[0]
                    self.screen_height = max_pos[1]
                    
                    # Restore original position
                    self.controller.position = current_pos
                except:
                    pass  # Keep defaults
        except Exception:
            # Keep default resolution if detection fails
            pass
        
        print(f"Detected screen resolution: {self.screen_width}x{self.screen_height}")
    
    def get_position(self) -> Tuple[int, int]:
        """Get current cursor position"""
        try:
            if self.controller:
                pos = self.controller.position
                return (int(pos[0]), int(pos[1]))
            elif self.x11_display:
                root = self.x11_display.screen().root
                pointer = root.query_pointer()
                return (pointer.root_x, pointer.root_y)
        except Exception:
            pass
        return (0, 0)
    
    def size(self) -> Tuple[int, int]:
        """Get screen size"""
        return (self.screen_width, self.screen_height)
    
    def move_to(self, position: List[int], steady: bool = False):
        """Move cursor with natural human behavior"""
        if len(position) != 2:
            return False
        
        target_x, target_y = int(position[0]), int(position[1])
        
        # Ensure target is within screen bounds
        target_x = max(0, min(self.screen_width - 1, target_x))
        target_y = max(0, min(self.screen_height - 1, target_y))
        
        current_pos = self.get_position()
        
        if steady:
            # Direct movement for steady mode
            return self._move_direct(target_x, target_y)
        else:
            # Human-like movement with natural behavior
            return self._move_human_like(current_pos, (target_x, target_y))
    
    def _move_human_like(self, start_pos: Tuple[int, int], target_pos: Tuple[int, int]) -> bool:
        """Move with natural human behavior"""
        try:
            # Calculate movement characteristics
            distance = math.sqrt((target_pos[0] - start_pos[0])**2 + (target_pos[1] - start_pos[1])**2)
            
            # Natural speed variation based on distance
            base_speed = 1.0
            if distance < 50:
                base_speed = 0.7  # Slower for precise movements
            elif distance > 500:
                base_speed = 1.3  # Faster for long movements
            
            # Add random speed variation
            speed = base_speed * (1 + random.uniform(-self.speed_variance, self.speed_variance))
            
            # Update fatigue (very gradual)
            session_time = time.time() - self.session_start
            self.fatigue_level = min(0.3, session_time / 7200)  # Max 30% fatigue over 2 hours
            speed *= (1 - self.fatigue_level * 0.5)  # Fatigue reduces speed
            
            # Generate natural curve
            generator = HumanizeMouseTrajectory()
            curve_points = generator.generate_curve(
                start_pos, target_pos, 
                curve_intensity=1 + random.uniform(-0.3, 0.3),
                speed_multiplier=speed
            )
            
            # Add natural human imperfections
            curve_points = self._add_human_imperfections(curve_points)
            
            # Natural pre-movement pause
            if random.random() < self.micro_pause_chance:
                time.sleep(random.uniform(0.05, 0.2))
            
            # Execute movement
            self._execute_curve_movement(curve_points)
            
            # Possible overshoot and correction
            if random.random() < self.error_chance:
                self._add_overshoot_correction(target_pos)
            
            # Update movement history
            self._update_movement_history(start_pos, target_pos)
            
            return True
            
        except Exception as e:
            print(f"Human-like movement error: {e}")
            return self._move_direct(target_pos[0], target_pos[1])
    
    def _add_human_imperfections(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Add natural human imperfections to movement"""
        if len(points) < 3:
            return points
        
        enhanced_points = []
        
        for i, (x, y) in enumerate(points):
            # Add micro-jitter (hand tremor)
            jitter_intensity = 0.5 + (self.fatigue_level * 0.5)
            jitter_x = random.gauss(0, jitter_intensity)
            jitter_y = random.gauss(0, jitter_intensity)
            
            # Reduce jitter at start and end of movement
            progress = i / (len(points) - 1) if len(points) > 1 else 0
            edge_factor = min(progress, 1 - progress) * 2
            jitter_x *= edge_factor
            jitter_y *= edge_factor
            
            enhanced_points.append((x + jitter_x, y + jitter_y))
            
            # Occasional hesitation (slow down)
            if i > 0 and i < len(points) - 1 and random.random() < 0.05:
                # Add duplicate point to create brief pause
                enhanced_points.append((x + jitter_x, y + jitter_y))
        
        return enhanced_points
    
    def _execute_curve_movement(self, points: List[Tuple[float, float]]):
        """Execute the movement curve naturally"""
        if not points:
            return
        
        for i, (x, y) in enumerate(points):
            try:
                # Ensure coordinates are within screen bounds
                x = max(0, min(self.screen_width - 1, int(x)))
                y = max(0, min(self.screen_height - 1, int(y)))
                
                # Move cursor
                if self.controller:
                    self.controller.position = (x, y)
                elif self.x11_display:
                    fake_input(self.x11_display, X.MotionNotify, x=x, y=y)
                    self.x11_display.sync()
                
                # Natural timing between points
                if i < len(points) - 1:
                    delay = 0.001 + random.uniform(0, 0.003)  # 1-4ms variation
                    delay *= (1 + self.fatigue_level * 0.5)   # Slower when fatigued
                    time.sleep(delay)
                    
            except Exception:
                continue  # Skip problematic points
    
    def _add_overshoot_correction(self, target_pos: Tuple[int, int]):
        """Add natural overshoot and correction"""
        if random.random() > self.correction_chance:
            return  # Don't correct this time
        
        try:
            # Small overshoot
            overshoot_distance = random.uniform(3, 12)
            angle = random.uniform(0, 2 * math.pi)
            
            overshoot_x = target_pos[0] + int(overshoot_distance * math.cos(angle))
            overshoot_y = target_pos[1] + int(overshoot_distance * math.sin(angle))
            
            # Ensure overshoot is within bounds
            overshoot_x = max(0, min(self.screen_width - 1, overshoot_x))
            overshoot_y = max(0, min(self.screen_height - 1, overshoot_y))
            
            # Move to overshoot position
            if self.controller:
                self.controller.position = (overshoot_x, overshoot_y)
            elif self.x11_display:
                fake_input(self.x11_display, X.MotionNotify, x=overshoot_x, y=overshoot_y)
                self.x11_display.sync()
            
            # Brief pause (realizing the overshoot)
            time.sleep(random.uniform(0.05, 0.15))
            
            # Correct back to target
            self._move_direct(target_pos[0], target_pos[1])
            
        except Exception:
            pass  # Fail silently if overshoot fails
    
    def _move_direct(self, x: int, y: int) -> bool:
        """Direct movement without human behavior"""
        try:
            # Ensure coordinates are within bounds
            x = max(0, min(self.screen_width - 1, x))
            y = max(0, min(self.screen_height - 1, y))
            
            if self.controller:
                self.controller.position = (x, y)
                return True
            elif self.x11_display:
                fake_input(self.x11_display, X.MotionNotify, x=x, y=y)
                self.x11_display.sync()
                return True
        except Exception as e:
            print(f"Direct move error: {e}")
            return False
        
        return False
    
    def _update_movement_history(self, start_pos: Tuple[int, int], target_pos: Tuple[int, int]):
        """Update movement history for natural patterns"""
        self.recent_moves.append((start_pos, target_pos, time.time()))
        
        # Keep only recent moves (last 20)
        if len(self.recent_moves) > 20:
            self.recent_moves = self.recent_moves[-20:]
    
    def click_on(self, position: List[int], button: str = "left", click_duration: float = 0.1):
        """Click with natural human timing"""
        if not self.move_to(position):
            return False
        
        # Natural pre-click pause
        if random.random() < 0.15:  # 15% chance
            time.sleep(random.uniform(0.05, 0.2))
        
        # Variable click duration
        duration = click_duration + random.uniform(-0.03, 0.05)
        duration = max(0.05, duration)  # Minimum duration
        
        return self.click(button, duration)
    
    def click(self, button: str = "left", duration: float = 0.1) -> bool:
        """Natural click with human timing"""
        try:
            mouse_button = getattr(Button, button, Button.left)
            
            if self.controller:
                self.controller.press(mouse_button)
                time.sleep(duration)
                self.controller.release(mouse_button)
                return True
            elif self.x11_display:
                button_code = 1 if button == "left" else 3 if button == "right" else 2
                fake_input(self.x11_display, X.ButtonPress, button_code)
                self.x11_display.sync()
                time.sleep(duration)
                fake_input(self.x11_display, X.ButtonRelease, button_code)
                self.x11_display.sync()
                return True
                
        except Exception as e:
            print(f"Click error: {e}")
            return False
        
        return False
    
    def scroll(self, clicks: int, direction: str = "down") -> bool:
        """Natural scrolling with human variation"""
        try:
            # Add natural variation to scroll speed
            scroll_delay = 0.1 + random.uniform(-0.03, 0.05)
            
            for i in range(abs(clicks)):
                if self.controller:
                    if direction == "down":
                        self.controller.scroll(0, -1)
                    else:
                        self.controller.scroll(0, 1)
                elif self.x11_display:
                    button_code = 5 if direction == "down" else 4
                    fake_input(self.x11_display, X.ButtonPress, button_code)
                    fake_input(self.x11_display, X.ButtonRelease, button_code)
                    self.x11_display.sync()
                
                if i < abs(clicks) - 1:  # Don't delay after last scroll
                    time.sleep(scroll_delay)
                    
            return True
            
        except Exception as e:
            print(f"Scroll error: {e}")
            return False
    
    def drag_to(self, start_position: List[int], end_position: List[int], button: str = "left") -> bool:
        """Natural drag operation"""
        try:
            # Move to start position
            if not self.move_to(start_position):
                return False
            
            # Natural pause before starting drag
            time.sleep(random.uniform(0.1, 0.3))
            
            # Press and hold
            mouse_button = getattr(Button, button, Button.left)
            
            if self.controller:
                self.controller.press(mouse_button)
            elif self.x11_display:
                button_code = 1 if button == "left" else 3 if button == "right" else 2
                fake_input(self.x11_display, X.ButtonPress, button_code)
                self.x11_display.sync()
            
            # Drag with human-like movement
            success = self.move_to(end_position)
            
            # Release
            if self.controller:
                self.controller.release(mouse_button)
            elif self.x11_display:
                fake_input(self.x11_display, X.ButtonRelease, button_code)
                self.x11_display.sync()
            
            return success
            
        except Exception as e:
            print(f"Drag error: {e}")
            return False