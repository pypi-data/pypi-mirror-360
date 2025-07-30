"""
Simple Human Curve Generator
Generates natural human-like movement curves without external dependencies
"""

import random
import math
from typing import List, Tuple


class HumanCurveGenerator:
    """Generates natural human-like mouse movement curves"""
    
    def __init__(self):
        pass
    
    def generate_curve(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                      curve_intensity: float = 1.0, speed_multiplier: float = 1.0) -> List[Tuple[float, float]]:
        """Generate a natural human-like curve between two points"""
        
        # Calculate basic movement parameters
        distance = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
        
        if distance < 3:
            # Very short movements - direct line
            return [(float(start_pos[0]), float(start_pos[1])), (float(end_pos[0]), float(end_pos[1]))]
        
        # Determine number of points based on distance
        num_points = max(10, min(100, int(distance / 3)))
        
        # Generate natural curve using simple bezier calculation
        curve_points = self._generate_bezier_curve(start_pos, end_pos, num_points, curve_intensity)
        
        return curve_points
    
    def _generate_bezier_curve(self, start: Tuple[int, int], end: Tuple[int, int], 
                              num_points: int, intensity: float) -> List[Tuple[float, float]]:
        """Generate a natural bezier curve"""
        
        # Calculate control points for natural human movement
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return [(float(start[0]), float(start[1]))]
        
        # Create natural control points
        # Control point 1: 1/3 along the path with perpendicular offset
        cp1_x = start[0] + dx * 0.33
        cp1_y = start[1] + dy * 0.33
        
        # Add perpendicular variation for natural curve
        perp_x = -dy / distance
        perp_y = dx / distance
        
        offset1 = random.uniform(-20, 20) * intensity
        cp1_x += perp_x * offset1
        cp1_y += perp_y * offset1
        
        # Control point 2: 2/3 along the path with different offset
        cp2_x = start[0] + dx * 0.67
        cp2_y = start[1] + dy * 0.67
        
        offset2 = random.uniform(-15, 15) * intensity
        cp2_x += perp_x * offset2
        cp2_y += perp_y * offset2
        
        # Generate curve points using cubic bezier
        curve_points = []
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0
            
            # Cubic bezier formula
            x = (1-t)**3 * start[0] + 3*(1-t)**2*t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * end[0]
            y = (1-t)**3 * start[1] + 3*(1-t)**2*t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * end[1]
            
            # Add micro-jitter for realism
            jitter_x = random.uniform(-0.5, 0.5)
            jitter_y = random.uniform(-0.5, 0.5)
            
            curve_points.append((x + jitter_x, y + jitter_y))
        
        # Ensure we end exactly at the target
        curve_points[-1] = (float(end[0]), float(end[1]))
        
        return curve_points