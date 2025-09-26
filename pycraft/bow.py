import pygame
import math
import time
from settings import BOW_TILT_ANGLE, BOW_OFFSET, BOW_CHARGE_TIME, BOW_SHAKE_INTENSITY, BOW_SHAKE_FREQUENCY
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
        
    def update(self, player_rect, right_click, camera, charge_time=0):
        """Update bow position and rotation based on mouse position"""
        self.player_rect = player_rect
        self.is_drawn = right_click
        
        if not self.is_drawn:
            self.charge_power = 0.0
            self.shake_offset_x = 0
            self.shake_offset_y = 0
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
        
    def shoot_arrow(self):
        """Create and return a new arrow with current charge power"""
        if not self.player_rect:
            return None
            
        # Calculate arrow spawn position (slightly offset from player)
        arrow_x = self.player_rect.centerx + math.cos(self.angle) * BOW_OFFSET
        arrow_y = self.player_rect.centery + math.sin(self.angle) * BOW_OFFSET
        
        return Arrow(arrow_x, arrow_y, self.angle, self.arrow_image, self.charge_power)
        
    def reset(self):
        """Reset bow state"""
        self.angle = 0
        self.is_drawn = False
        self.charge_power = 0.0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
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