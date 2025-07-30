"""
Enhanced Human Behavior Simulation for Linux
Provides realistic human-like patterns for mouse movement and interaction
"""

import random
import time
import math
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class HumanProfile(Enum):
    """Different human behavior profiles"""
    CAREFUL = "careful"          # Slow, precise movements
    NORMAL = "normal"            # Average user behavior
    FAST = "fast"               # Quick, efficient movements
    ERRATIC = "erratic"         # Unpredictable patterns
    GAMING = "gaming"           # Gaming-optimized patterns


@dataclass
class HumanBehaviorConfig:
    """Configuration for human-like behavior"""
    profile: HumanProfile = HumanProfile.NORMAL
    
    # Movement characteristics
    base_speed: float = 1.0
    speed_variance: float = 0.3
    
    # Pause patterns
    micro_pause_chance: float = 0.15    # Small hesitations
    thinking_pause_chance: float = 0.08  # Longer pauses
    
    # Error simulation
    overshoot_chance: float = 0.12      # Mouse overshoots target
    correction_chance: float = 0.18     # Minor corrections
    
    # Fatigue simulation
    fatigue_factor: float = 0.0         # Increases over time
    max_fatigue: float = 0.3
    
    # Distraction simulation
    distraction_chance: float = 0.05    # Random movements away from target
    
    # Click patterns
    double_click_detection: bool = True
    click_pressure_variance: bool = True


class HumanBehaviorSimulator:
    """Simulates realistic human mouse behavior patterns"""
    
    def __init__(self, config: Optional[HumanBehaviorConfig] = None):
        self.config = config or HumanBehaviorConfig()
        self.session_start = time.time()
        self.action_count = 0
        self.last_position = (0, 0)
        self.fatigue_level = 0.0
        self.recent_actions = []
        
    def get_movement_params(self, from_point: Tuple[int, int], 
                          to_point: Tuple[int, int]) -> Dict[str, Any]:
        """Get human-like movement parameters"""
        distance = math.sqrt((to_point[0] - from_point[0])**2 + 
                           (to_point[1] - from_point[1])**2)
        
        # Base parameters influenced by profile
        params = self._get_profile_params()
        
        # Adjust for distance
        params.update(self._adjust_for_distance(distance))
        
        # Apply fatigue effects
        params.update(self._apply_fatigue_effects(params))
        
        # Add behavioral quirks
        params.update(self._add_behavioral_quirks(from_point, to_point))
        
        return params
    
    def _get_profile_params(self) -> Dict[str, Any]:
        """Get base parameters for current profile"""
        profile_configs = {
            HumanProfile.CAREFUL: {
                'speed_multiplier': 0.7,
                'precision': 0.9,
                'hesitation_chance': 0.25,
                'overshoot_reduction': 0.5
            },
            HumanProfile.NORMAL: {
                'speed_multiplier': 1.0,
                'precision': 0.75,
                'hesitation_chance': 0.15,
                'overshoot_reduction': 1.0
            },
            HumanProfile.FAST: {
                'speed_multiplier': 1.4,
                'precision': 0.6,
                'hesitation_chance': 0.05,
                'overshoot_reduction': 1.3
            },
            HumanProfile.ERRATIC: {
                'speed_multiplier': random.uniform(0.5, 1.8),
                'precision': random.uniform(0.3, 0.9),
                'hesitation_chance': random.uniform(0.1, 0.4),
                'overshoot_reduction': random.uniform(0.8, 1.5)
            },
            HumanProfile.GAMING: {
                'speed_multiplier': 1.6,
                'precision': 0.85,
                'hesitation_chance': 0.02,
                'overshoot_reduction': 0.8
            }
        }
        
        return profile_configs[self.config.profile]
    
    def _adjust_for_distance(self, distance: float) -> Dict[str, Any]:
        """Adjust parameters based on movement distance"""
        if distance < 50:
            # Short movements - more precise
            return {
                'curve_complexity': random.randint(1, 2),
                'distortion_factor': 0.5,
                'speed_variance': 0.1
            }
        elif distance < 200:
            # Medium movements - normal behavior
            return {
                'curve_complexity': random.randint(2, 4),
                'distortion_factor': 1.0,
                'speed_variance': 0.3
            }
        else:
            # Long movements - more curve variation
            return {
                'curve_complexity': random.randint(3, 6),
                'distortion_factor': 1.5,
                'speed_variance': 0.4
            }
    
    def _apply_fatigue_effects(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply fatigue effects to movement"""
        # Increase fatigue over time
        session_time = time.time() - self.session_start
        self.fatigue_level = min(self.config.max_fatigue, 
                               session_time / 3600 * 0.1)  # 10% fatigue per hour
        
        if self.fatigue_level > 0:
            # Fatigue reduces precision and increases hesitation
            params['precision'] *= (1 - self.fatigue_level)
            params['hesitation_chance'] += self.fatigue_level * 0.2
            params['speed_multiplier'] *= (1 - self.fatigue_level * 0.3)
            
        return params
    
    def _add_behavioral_quirks(self, from_point: Tuple[int, int], 
                             to_point: Tuple[int, int]) -> Dict[str, Any]:
        """Add realistic behavioral quirks"""
        quirks = {}
        
        # Momentum effects - continuing in same direction is faster
        if len(self.recent_actions) >= 2:
            prev_vector = self._get_movement_vector(self.recent_actions[-2], 
                                                  self.recent_actions[-1])
            curr_vector = self._get_movement_vector(from_point, to_point)
            
            # Calculate angle between movements
            angle = self._calculate_angle(prev_vector, curr_vector)
            
            if angle < 30:  # Similar direction
                quirks['momentum_bonus'] = 1.2
            elif angle > 150:  # Opposite direction
                quirks['direction_change_penalty'] = 0.8
                
        # Add micro-corrections for realism
        if random.random() < self.config.correction_chance:
            quirks['add_micro_correction'] = True
            
        # Add distraction movements
        if random.random() < self.config.distraction_chance:
            quirks['add_distraction'] = True
            
        return quirks
    
    def _get_movement_vector(self, p1: Tuple[int, int], 
                           p2: Tuple[int, int]) -> Tuple[float, float]:
        """Get normalized movement vector"""
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return (0, 0)
            
        return (dx/length, dy/length)
    
    def _calculate_angle(self, v1: Tuple[float, float], 
                        v2: Tuple[float, float]) -> float:
        """Calculate angle between two vectors in degrees"""
        dot_product = v1[0]*v2[0] + v1[1]*v2[1]
        dot_product = max(-1, min(1, dot_product))  # Clamp to valid range
        angle_rad = math.acos(dot_product)
        return math.degrees(angle_rad)
    
    def should_add_pause(self) -> Optional[float]:
        """Determine if a pause should be added and for how long"""
        # Micro pauses
        if random.random() < self.config.micro_pause_chance:
            return random.uniform(0.05, 0.2)
            
        # Thinking pauses
        if random.random() < self.config.thinking_pause_chance:
            return random.uniform(0.3, 1.2)
            
        return None
    
    def should_add_overshoot(self, target: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Determine if mouse should overshoot target"""
        if random.random() < self.config.overshoot_chance:
            # Overshoot by 5-20 pixels in random direction
            overshoot_distance = random.uniform(5, 20)
            angle = random.uniform(0, 2 * math.pi)
            
            overshoot_x = target[0] + int(overshoot_distance * math.cos(angle))
            overshoot_y = target[1] + int(overshoot_distance * math.sin(angle))
            
            return (overshoot_x, overshoot_y)
            
        return None
    
    def get_click_variations(self) -> Dict[str, Any]:
        """Get human-like click variations"""
        variations = {}
        
        # Click duration variations
        base_duration = 0.1
        if self.config.click_pressure_variance:
            variations['click_duration'] = base_duration + random.uniform(-0.05, 0.1)
        else:
            variations['click_duration'] = base_duration
            
        # Pre-click hesitation
        if random.random() < 0.1:
            variations['pre_click_pause'] = random.uniform(0.05, 0.3)
            
        return variations
    
    def update_action_history(self, action_type: str, position: Tuple[int, int]):
        """Update action history for learning patterns"""
        self.action_count += 1
        self.last_position = position
        
        # Keep last 10 actions for pattern analysis
        self.recent_actions.append(position)
        if len(self.recent_actions) > 10:
            self.recent_actions.pop(0)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return {
            'session_duration': time.time() - self.session_start,
            'action_count': self.action_count,
            'fatigue_level': self.fatigue_level,
            'profile': self.config.profile.value,
            'avg_actions_per_minute': self.action_count / max(1, (time.time() - self.session_start) / 60)
        }


class HumanMovementEnhancer:
    """Enhances movement curves with human-like characteristics"""
    
    @staticmethod
    def add_human_jitter(points: List[Tuple[float, float]], 
                        intensity: float = 1.0) -> List[Tuple[float, float]]:
        """Add subtle jitter to movement points"""
        enhanced_points = []
        
        for i, (x, y) in enumerate(points):
            # Add micro-movements (hand tremor simulation)
            jitter_x = random.gauss(0, intensity * 0.5)
            jitter_y = random.gauss(0, intensity * 0.5)
            
            # Reduce jitter at start and end
            progress = i / max(1, len(points) - 1)
            edge_reduction = min(progress, 1 - progress) * 2
            jitter_x *= edge_reduction
            jitter_y *= edge_reduction
            
            enhanced_points.append((x + jitter_x, y + jitter_y))
            
        return enhanced_points
    
    @staticmethod
    def add_hesitation_points(points: List[Tuple[float, float]], 
                            hesitation_chance: float = 0.1) -> List[Tuple[float, float]]:
        """Add hesitation points where mouse slows down"""
        if random.random() > hesitation_chance:
            return points
            
        enhanced_points = []
        hesitation_index = random.randint(len(points) // 4, 3 * len(points) // 4)
        
        for i, point in enumerate(points):
            enhanced_points.append(point)
            
            # Add hesitation near the chosen index
            if abs(i - hesitation_index) <= 2:
                # Duplicate nearby points to create slowdown
                enhanced_points.append(point)
                if abs(i - hesitation_index) <= 1:
                    enhanced_points.append(point)
                    
        return enhanced_points
    
    @staticmethod
    def add_correction_movement(target: Tuple[int, int], 
                              overshoot: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Generate correction movement from overshoot back to target"""
        # Create a small curve back to target
        correction_points = []
        
        # Add intermediate point for more natural correction
        mid_x = overshoot[0] + (target[0] - overshoot[0]) * 0.7
        mid_y = overshoot[1] + (target[1] - overshoot[1]) * 0.7
        
        # Add slight curve to correction
        perpendicular_offset = random.uniform(-3, 3)
        dx = target[0] - overshoot[0]
        dy = target[1] - overshoot[1]
        
        if dx != 0 or dy != 0:
            length = math.sqrt(dx*dx + dy*dy)
            perp_x = -dy / length * perpendicular_offset
            perp_y = dx / length * perpendicular_offset
            
            mid_x += perp_x
            mid_y += perp_y
        
        correction_points.extend([
            overshoot,
            (int(mid_x), int(mid_y)),
            target
        ])
        
        return correction_points


def create_human_behavior_demo() -> str:
    """Create demonstration script showing human behavior"""
    demo_script = '''#!/usr/bin/env python3
"""
Human Behavior Demonstration Script
Shows realistic human-like mouse movement patterns
"""

import time
from humancursor import SystemCursor
from humancursor.utilities.human_behavior import (
    HumanBehaviorSimulator, HumanProfile, HumanBehaviorConfig
)

def demonstrate_human_profiles():
    """Demonstrate different human behavior profiles"""
    cursor = SystemCursor()
    
    profiles = [
        (HumanProfile.CAREFUL, "Careful user - slow, precise movements"),
        (HumanProfile.NORMAL, "Normal user - average behavior"),
        (HumanProfile.FAST, "Fast user - quick, efficient movements"),
        (HumanProfile.ERRATIC, "Erratic user - unpredictable patterns"),
        (HumanProfile.GAMING, "Gaming user - optimized for speed and precision")
    ]
    
    print("=== Human Behavior Profile Demonstration ===\\n")
    
    for profile, description in profiles:
        print(f"Testing {profile.value.upper()} profile: {description}")
        
        # Create behavior simulator with specific profile
        config = HumanBehaviorConfig(profile=profile)
        behavior = HumanBehaviorSimulator(config)
        
        # Test movement pattern
        start_pos = [200, 200]
        targets = [
            [400, 300], [600, 250], [500, 400], 
            [300, 450], [250, 300], [200, 200]
        ]
        
        cursor.move_to(start_pos)
        time.sleep(1)
        
        for target in targets:
            # Get human-like movement parameters
            params = behavior.get_movement_params(cursor.get_position(), tuple(target))
            
            # Check for pauses
            pause_duration = behavior.should_add_pause()
            if pause_duration:
                print(f"  Adding human pause: {pause_duration:.2f}s")
                time.sleep(pause_duration)
            
            # Check for overshoot
            overshoot = behavior.should_add_overshoot(tuple(target))
            if overshoot:
                print(f"  Overshooting target, then correcting...")
                cursor.move_to(list(overshoot), steady=False)
                time.sleep(0.1)
                cursor.move_to(target, steady=True)
            else:
                cursor.move_to(target, steady=False)
            
            # Update behavior history
            behavior.update_action_history("move", tuple(target))
            
            time.sleep(0.3)
        
        # Show session stats
        stats = behavior.get_session_stats()
        print(f"  Session stats: {stats['action_count']} actions, "
              f"fatigue: {stats['fatigue_level']:.2f}")
        print()
        
        time.sleep(2)  # Pause between profiles

def demonstrate_realistic_clicking():
    """Demonstrate human-like clicking patterns"""
    cursor = SystemCursor()
    behavior = HumanBehaviorSimulator()
    
    print("=== Realistic Clicking Demonstration ===\\n")
    
    click_targets = [
        ([300, 300], "Single click with hesitation"),
        ([500, 300], "Quick click"),
        ([400, 400], "Click with overshoot correction"),
        ([300, 500], "Pressured click (longer duration)")
    ]
    
    for target, description in click_targets:
        print(f"Demonstrating: {description}")
        
        # Move to target with human behavior
        cursor.move_to(target)
        
        # Get click variations
        click_vars = behavior.get_click_variations()
        
        # Pre-click pause
        if 'pre_click_pause' in click_vars:
            time.sleep(click_vars['pre_click_pause'])
            
        # Perform click with human duration
        cursor.click_on(target, click_duration=click_vars['click_duration'])
        
        time.sleep(1)

if __name__ == '__main__':
    print("Starting Human Behavior Demonstration...")
    print("This will show realistic human-like mouse movements and clicking patterns.\\n")
    
    try:
        demonstrate_human_profiles()
        demonstrate_realistic_clicking()
        print("Demonstration completed!")
        
    except KeyboardInterrupt:
        print("\\nDemonstration interrupted by user")
    except Exception as e:
        print(f"Error during demonstration: {e}")
'''
    
    return demo_script