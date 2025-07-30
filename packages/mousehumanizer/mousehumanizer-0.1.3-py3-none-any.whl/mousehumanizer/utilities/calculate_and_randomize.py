"""
Simple calculation and randomization utilities
Provides natural human timing and movement calculations
"""

import random
import math
import time
from typing import Tuple


def calculate_and_randomize(distance: float) -> Tuple[float, float]:
    """Calculate natural human timing and speed variation"""
    
    # Base timing calculation (pixels per second)
    base_speed = 800  # pixels per second
    
    # Adjust speed based on distance
    if distance < 50:
        # Short movements are more precise/slower
        speed_multiplier = 0.7
    elif distance > 500:
        # Long movements are faster
        speed_multiplier = 1.3
    else:
        # Medium movements
        speed_multiplier = 1.0
    
    # Add natural variation
    speed_variance = random.uniform(0.7, 1.3)
    final_speed = base_speed * speed_multiplier * speed_variance
    
    # Calculate duration
    duration = distance / final_speed
    
    # Add minimum duration for very short movements
    duration = max(0.1, duration)
    
    # Random delay for natural hesitation
    delay = 0.0
    if random.random() < 0.1:  # 10% chance
        delay = random.uniform(0.05, 0.3)
    
    return duration, delay


def get_natural_timing() -> float:
    """Get natural timing variation for movements"""
    return random.uniform(0.001, 0.005)  # 1-5ms variation


def calculate_curve_parameters(start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> dict:
    """Calculate parameters for natural curve generation"""
    
    distance = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
    
    # Natural curve intensity based on distance
    if distance < 30:
        curve_intensity = 0.3  # Very subtle for short movements
    elif distance < 100:
        curve_intensity = 0.8  # Moderate curve
    else:
        curve_intensity = 1.2  # More pronounced for long movements
    
    # Add randomness
    curve_intensity *= random.uniform(0.7, 1.3)
    
    return {
        'curve_intensity': curve_intensity,
        'distance': distance,
        'num_points': max(10, min(100, int(distance / 3)))
    }