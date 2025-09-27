import pygame
import math
import time
from settings import BOW_TILT_ANGLE, BOW_OFFSET, BOW_CHARGE_TIME, BOW_SHAKE_INTENSITY, BOW_SHAKE_FREQUENCY, BOW_ARROW_OFFSET, BOW_ARROW_SCALE
from arrow import Arrow

class Bow:
    def __init__(self, image, arrow_image):
        self.image = image
        self.arrow_image = arrow_image
        self.angle = 0
        self.player_rect = None
        self.is_drawn = False  # Only show when right click is held
        self.charge_start_time = 0
        self.charge_power = 0.0  # 0.0 to 1.0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.is_charging = False  # Track if charging for arrow animation
        
        # Create scaled and blue-tinted arrow for bow animation
        if arrow_image:
            arrow_h = int(arrow_image.get_height() * BOW_ARROW_SCALE)
            arrow_w = int(arrow_image.get_width() * BOW_ARROW_SCALE)
            scaled_arrow = pygame.transform.scale(arrow_image, (arrow_w, arrow_h))
            # Apply blue tint
            self.bow_arrow_image = self.apply_blue_tint_to_bow_arrow(scaled_arrow)
        else:
            self.bow_arrow_image = None
        
    def update(self, player_rect, right_click, camera, charge_time=0):
        """Update bow position and rotation based on mouse position"""
        self.player_rect = player_rect
        self.is_drawn = right_click
        self.is_charging = charge_time > 0  # Track if actively charging
        
        if not self.is_drawn:
            self.charge_power = 0.0
            self.shake_offset_x = 0
            self.shake_offset_y = 0
            self.is_charging = False
            return
        
        # Calculate charge power based on how long right click has been held
        self.charge_power = min(charge_time / BOW_CHARGE_TIME, 1.0)
        
        # Calculate shake effect based on charge power
        if self.charge_power > 0:
            shake_intensity = self.charge_power * BOW_SHAKE_INTENSITY
            shake_time = time.time() / BOW_SHAKE_FREQUENCY
            self.shake_offset_x = math.sin(shake_time * 10) * shake_intensity
            self.shake_offset_y = math.cos(shake_time * 12) * shake_intensity
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Get world mouse position (accounting for camera)
        # Convert screen coordinates to world coordinates
        world_mouse_x = mouse_pos[0] - camera.camera.left
        world_mouse_y = mouse_pos[1] - camera.camera.top
        
        # Calculate angle from player to mouse
        dx = world_mouse_x - player_rect.centerx
        dy = world_mouse_y - player_rect.centery
        self.angle = math.atan2(dy, dx)
        
    def shoot_arrow(self, enemy=None):
        """Create and return a new arrow with current charge power and slight aimbot assist"""
        if not self.player_rect:
            return None
            
        # Calculate arrow spawn position at the edge of the character
        # Use character radius to spawn arrow right outside the player
        character_radius = max(self.player_rect.width, self.player_rect.height) // 2
        arrow_x = self.player_rect.centerx + math.cos(self.angle) * character_radius
        arrow_y = self.player_rect.centery + math.sin(self.angle) * character_radius
        
        # Apply slight aimbot assist if enemy is provided
        final_angle = self.angle
        if enemy and hasattr(enemy, 'rect'):
            # Calculate angle to enemy
            dx = enemy.rect.centerx - arrow_x
            dy = enemy.rect.centery - arrow_y
            angle_to_enemy = math.atan2(dy, dx)
            
            # Calculate angle difference
            angle_diff = angle_to_enemy - self.angle
            # Normalize angle difference to [-pi, pi]
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Apply small correction (max 15 degrees = ~0.26 radians)
            max_assist = math.radians(15)  # 15 degree max assist
            assist_amount = max(-max_assist, min(max_assist, angle_diff * 0.3))  # 30% of the angle diff, capped
            final_angle = self.angle + assist_amount
        
        return Arrow(arrow_x, arrow_y, final_angle, self.arrow_image, self.charge_power)
        
    def reset(self):
        """Reset bow state"""
        self.angle = 0
        self.is_drawn = False
        self.charge_power = 0.0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.is_charging = False
        
    def draw(self, screen, camera):
        """Draw the bow at the player's position (only when drawn)"""
        if not self.player_rect or not self.is_drawn:
            return
        
        # Position bow with a slight offset towards the cursor and add shake
        bow_x = self.player_rect.centerx + math.cos(self.angle) * BOW_OFFSET + self.shake_offset_x
        bow_y = self.player_rect.centery + math.sin(self.angle) * BOW_OFFSET + self.shake_offset_y
        
        # Apply camera transform to get screen position
        screen_pos = camera.apply_point((bow_x, bow_y))
        
        # Determine if we need to flip the image and add rotation offset
        is_flipped = False
        rotation_offset = 0
        angle_degrees = math.degrees(self.angle)
        
        if abs(angle_degrees) < 90:  # Right side
            is_flipped = True
            rotation_offset = BOW_TILT_ANGLE  # Use setting for right side
        else:  # Left side
            rotation_offset = -BOW_TILT_ANGLE  # Use setting for left side

        # Rotate bow image to point toward mouse with additional offset
        image_to_rotate = pygame.transform.flip(self.image, is_flipped, False)
        rotated_bow = pygame.transform.rotate(image_to_rotate, -angle_degrees - 90 + rotation_offset)
        bow_rect = rotated_bow.get_rect(center=screen_pos)
        
        # Draw the bow
        screen.blit(rotated_bow, bow_rect)
        
        # Draw arrow if charging
        if self.is_charging and self.bow_arrow_image:
            self.draw_bow_arrow(screen, camera, bow_x, bow_y, angle_degrees, is_flipped)
            
    def apply_blue_tint_to_bow_arrow(self, image):
        """Apply blue tint to the bow arrow"""
        # Create a surface with blue tint
        tint_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        tint_surface.fill((100, 150, 255, 128))  # Blue tint with alpha
        
        # Create a copy and blend
        tinted_image = image.copy()
        tinted_image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return tinted_image
        
    def draw_bow_arrow(self, screen, camera, bow_x, bow_y, angle_degrees, is_flipped):
        """Draw the arrow being held in the bow"""
        # Calculate arrow position (pulled back based on charge)
        pullback_distance = BOW_ARROW_OFFSET * self.charge_power
        
        # Position arrow behind the bow center
        arrow_x = bow_x - math.cos(self.angle) * pullback_distance
        arrow_y = bow_y - math.sin(self.angle) * pullback_distance
        
        # Apply camera transform
        screen_arrow_pos = camera.apply_point((arrow_x, arrow_y))
        
        # Rotate arrow to match bow angle (don't flip the arrow, only rotate)
        rotated_arrow = pygame.transform.rotate(self.bow_arrow_image, -angle_degrees)  # Match bow direction exactly
        arrow_rect = rotated_arrow.get_rect(center=screen_arrow_pos)
        
        # Draw the arrow
        screen.blit(rotated_arrow, arrow_rect)