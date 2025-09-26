import pygame
import math
from settings import ARROW_BASE_SPEED, ARROW_MAX_SPEED, ARROW_GRAVITY, ARROW_BLUE_TINT, ARROW_TRAIL_COLOR
from trail import Trail

class Arrow:
    def __init__(self, x, y, angle, image, power=1.0):
        self.original_image = image
        # Apply blue tint to the arrow
        self.image = self.apply_blue_tint(image.copy())
        self.rect = self.image.get_rect(center=(x, y))
        
        # Calculate speed based on power (0.0 to 1.0)
        arrow_speed = ARROW_BASE_SPEED + (ARROW_MAX_SPEED - ARROW_BASE_SPEED) * power
        
        # Physics
        self.vel_x = math.cos(angle) * arrow_speed
        self.vel_y = math.sin(angle) * arrow_speed
        self.angle = angle
        self.alive = True
        
        # Trail effect
        self.trail = Trail(ARROW_TRAIL_COLOR)
        self.trail.add_position(x, y)  # Add initial position
        
    def apply_blue_tint(self, image):
        """Apply a blue tint to the arrow image"""
        # Create a surface with the blue tint color
        tint_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        tint_surface.fill(ARROW_BLUE_TINT + (128,))  # Add alpha for blending
        
        # Create a copy of the original image
        tinted_image = image.copy()
        # Blend the tint with the original image
        tinted_image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return tinted_image
        
    def update(self, platforms):
        """Update arrow physics and collision"""
        if not self.alive:
            return
            
        # Apply gravity
        self.vel_y += ARROW_GRAVITY
        
        # Update position
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Update rotation based on velocity BEFORE adding to trail
        self.angle = math.atan2(self.vel_y, self.vel_x)
        
        # Add current position to trail (use center of arrow)
        self.trail.add_position(self.rect.centerx, self.rect.centery)
        
        # Check collision with platforms
        for platform in platforms:
            if self.rect.colliderect(platform):
                self.alive = False
                break
                
        # Remove arrow if it goes way off screen (very generous boundaries)
        # This prevents arrows from existing forever but allows for large world coordinates
        if (self.rect.centerx < -1000 or self.rect.centerx > 20000 or 
            self.rect.centery < -1000 or self.rect.centery > 5000):
            self.alive = False
            
    def draw(self, screen, camera):
        """Draw the arrow on screen"""
        if not self.alive:
            return
            
        # Draw trail first (behind the arrow)
        self.trail.draw(screen, camera)
        
        # Rotate the arrow image based on its trajectory
        angle_degrees = math.degrees(self.angle)
        rotated_arrow = pygame.transform.rotate(self.image, -angle_degrees)
        arrow_rect = rotated_arrow.get_rect(center=self.rect.center)
        
        # Apply camera transform and draw
        screen.blit(rotated_arrow, camera.apply(arrow_rect))