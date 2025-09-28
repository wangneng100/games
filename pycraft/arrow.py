import pygame
import math
from settings import ARROW_BASE_SPEED, ARROW_MAX_SPEED, ARROW_GRAVITY, ARROW_BLUE_TINT, ARROW_TRAIL_COLOR, ARROW_PIERCE_COUNT, ARROW_PARTICLE_COLOR, PARTICLE_COUNT
from trail import Trail

class Arrow:
    def __init__(self, x, y, angle, image, power=1.0):
        self.original_image = image
        # Apply blue tint to the arrow (can be overridden)
        self.image = self.apply_blue_tint(image.copy())
        self.rect = self.image.get_rect(center=(x, y))
        
        # Calculate speed based on power (0.0 to 1.0)
        arrow_speed = ARROW_BASE_SPEED + (ARROW_MAX_SPEED - ARROW_BASE_SPEED) * power
        
        # Physics
        self.vel_x = math.cos(angle) * arrow_speed
        self.vel_y = math.sin(angle) * arrow_speed
        self.angle = angle
        self.alive = True
        self.blocks_pierced = 0  # Track how many blocks have been pierced
        self.charge_power = power  # Store charge power for damage calculation
        
        # Enemy arrow properties
        self.color = None  # Custom color for enemy arrows
        self.damage = 15  # Default damage
        self.is_enemy_arrow = False
        
        # Trail effect
        self.trail = Trail(ARROW_TRAIL_COLOR)
        self.trail.add_position(x, y)  # Add initial position
        self.particle_system = None  # Will be set by player
        
        # SUPER MOTION BLUR for arrows
        self.motion_blur_copies = []  # Store arrow positions for blur
        self.max_blur_copies = 400  # EVEN MORE copies for arrows (they're fast!)
        self.blur_alpha_decay = 0.94  # Much smoother, slower fade
        
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
        
    def set_color(self, color):
        """Set custom color for enemy arrows"""
        self.color = color
        if color:
            # Apply custom color tint
            tint_surface = pygame.Surface(self.original_image.get_size(), pygame.SRCALPHA)
            tint_surface.fill(color + (128,))  # Add alpha for blending
            
            self.image = self.original_image.copy()
            self.image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
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
        
        # SUPER MOTION BLUR UPDATE for arrows
        arrow_speed = math.sqrt(self.vel_x**2 + self.vel_y**2)
        if arrow_speed > 1.0:  # Only add blur when moving fast
            # Dynamic blur count based on speed (faster arrows = MORE BLUR!)
            speed_multiplier = min(arrow_speed / 8.0, 4.0)  # Cap at 4x multiplier
            dynamic_max_copies = int(self.max_blur_copies * speed_multiplier)
            dynamic_max_copies = max(30, dynamic_max_copies)  # Minimum 30 copies
            
            # Add current position to blur trail
            if len(self.motion_blur_copies) >= dynamic_max_copies:
                self.motion_blur_copies.pop(0)  # Remove oldest copy
            
            # Store position, angle, and alpha for blur effect
            alpha = 28  # Even much lighter (85/3 = 28)
            self.motion_blur_copies.append({
                'x': self.rect.centerx,
                'y': self.rect.centery,
                'angle': self.angle,
                'alpha': alpha,
                'image': self.image.copy()
            })
        
        # Fade existing blur copies
        for i in range(len(self.motion_blur_copies) - 1, -1, -1):
            copy = self.motion_blur_copies[i]
            copy['alpha'] *= self.blur_alpha_decay
            if copy['alpha'] < 8:  # Remove very faded copies
                self.motion_blur_copies.pop(i)
        
        # Check collision with platforms (with piercing) - more accurate collision
        arrow_center = pygame.Rect(self.rect.centerx - 4, self.rect.centery - 4, 8, 8)
        for platform in platforms:
            if arrow_center.colliderect(platform):
                if self.blocks_pierced < ARROW_PIERCE_COUNT:
                    self.blocks_pierced += 1
                    # Reduce speed when piercing
                    self.vel_x *= 0.7
                    self.vel_y *= 0.7
                    # Create small particle effect when piercing
                    if hasattr(self, 'particle_system') and self.particle_system:
                        self.particle_system.create_explosion(
                            self.rect.centerx, self.rect.centery, 
                            ARROW_PARTICLE_COLOR, count=4
                        )
                    # Move arrow slightly forward to avoid getting stuck
                    self.rect.x += self.vel_x * 0.5
                    self.rect.y += self.vel_y * 0.5
                else:
                    # Create particle explosion when arrow dies
                    if hasattr(self, 'particle_system') and self.particle_system:
                        self.particle_system.create_explosion(
                            self.rect.centerx, self.rect.centery, 
                            ARROW_PARTICLE_COLOR, count=PARTICLE_COUNT
                        )
                    self.alive = False
                    break
                
        # Remove arrow if it goes way off screen (very generous boundaries)
        # This prevents arrows from existing forever but allows for large world coordinates
        if (self.rect.centerx < -1000 or self.rect.centerx > 20000 or 
            self.rect.centery < -1000 or self.rect.centery > 5000):
            self.alive = False
            
    def draw(self, screen, camera):
        """Draw the arrow on screen with SUPER MOTION BLUR"""
        if not self.alive:
            return
            
        # Draw trail first (behind the arrow)
        self.trail.draw(screen, camera)
        
        # DRAW MOTION BLUR COPIES FIRST (behind main arrow)
        for copy in self.motion_blur_copies:
            if copy['alpha'] > 8:  # Only draw visible copies
                # Rotate the blur copy
                blur_angle_degrees = math.degrees(copy['angle'])
                blur_rotated = pygame.transform.rotate(copy['image'], -blur_angle_degrees)
                blur_rect = blur_rotated.get_rect(center=(copy['x'], copy['y']))
                
                # Apply alpha transparency for blur effect
                blur_surface = blur_rotated.copy()
                blur_surface.set_alpha(int(copy['alpha']))
                
                # Draw the blur copy
                screen.blit(blur_surface, camera.apply(blur_rect))
        
        # Rotate the arrow image based on its trajectory
        angle_degrees = math.degrees(self.angle)
        rotated_arrow = pygame.transform.rotate(self.image, -angle_degrees)
        arrow_rect = rotated_arrow.get_rect(center=self.rect.center)
        
        # Draw arrow normally without brightness overlay
        screen.blit(rotated_arrow, camera.apply(arrow_rect))