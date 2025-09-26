import pygame
import math
from settings import TRAIL_LENGTH, TRAIL_FADE_RATE, TRAIL_WIDTH

class Trail:
    def __init__(self, color, max_length=TRAIL_LENGTH, use_shade=False):
        self.color = color
        self.max_length = max_length
        self.positions = []  # List of (x, y) positions
        self.fade_rate = TRAIL_FADE_RATE
        self.use_shade = use_shade
        self.shade_color = (80, 80, 80)  # Default shade color if needed
        
    def add_position(self, x, y):
        """Add a new position to the trail"""
        self.positions.append((x, y))
        
        # Remove old positions if trail is too long
        if len(self.positions) > self.max_length:
            self.positions.pop(0)
            
    def update(self):
        """Update the trail (mainly for cleanup)"""
        # Trail positions are managed by add_position
        pass
        
    def clear(self):
        """Clear all trail positions"""
        self.positions.clear()
        
    def draw(self, screen, camera):
        """Draw the trail on screen"""
        if len(self.positions) < 2:
            return
            
        # Draw trail segments with fading effect
        for i in range(len(self.positions) - 1):
            start_pos = self.positions[i]
            end_pos = self.positions[i + 1]
            
            # Calculate alpha based on position in trail (newer = more opaque)
            alpha_factor = (i + 1) / len(self.positions)
            alpha = int(255 * alpha_factor)
            
            # Create color with alpha
            trail_color = (*self.color, alpha)
            
            # Apply camera transform
            screen_start = camera.apply_point(start_pos)
            screen_end = camera.apply_point(end_pos)
            
            # Fast trail drawing - no transparency to avoid lag
            if alpha > 10:  # Draw even more segments for smoother trail
                # Calculate line thickness based on trail position (thinner for more transparency effect)
                thickness = max(1, int(TRAIL_WIDTH * alpha_factor * 0.7))
                
                # Much lighter and more transparent appearance
                brightness = 0.8 + (alpha_factor * 0.2)  # Range from 0.8 to 1.0 (very bright)
                trail_color = (
                    int(self.color[0] * brightness),
                    int(self.color[1] * brightness), 
                    int(self.color[2] * brightness)
                )
                
                # Simple, fast line drawing
                try:
                    pygame.draw.line(screen, trail_color, screen_start, screen_end, thickness)
                except:
                    pass

class TrailManager:
    """Manages multiple trails for different objects"""
    def __init__(self):
        self.trails = {}
        
    def add_trail(self, object_id, color, max_length=TRAIL_LENGTH):
        """Add a new trail for an object"""
        self.trails[object_id] = Trail(color, max_length)
        
    def update_trail(self, object_id, x, y):
        """Update trail position for an object"""
        if object_id in self.trails:
            self.trails[object_id].add_position(x, y)
            
    def clear_trail(self, object_id):
        """Clear trail for an object"""
        if object_id in self.trails:
            self.trails[object_id].clear()
            
    def remove_trail(self, object_id):
        """Remove trail for an object"""
        if object_id in self.trails:
            del self.trails[object_id]
            
    def draw_all(self, screen, camera):
        """Draw all trails"""
        for trail in self.trails.values():
            trail.draw(screen, camera)
            
    def update_all(self):
        """Update all trails"""
        for trail in self.trails.values():
            trail.update()