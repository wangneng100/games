import pygame
import math
from settings import STAFF_TILT_ANGLE, STAFF_OFFSET

class Staff:
    def __init__(self, image, color):
        self.image = image
        self.color = color
        self.angle = 0
        self.prev_angle = 0
        self.length = 100
        self.player_rect = None
        self.is_swinging = False
        
    def update(self, player_rect, left_click, platforms, camera, player_vel):
        """Update staff position and rotation based on mouse position"""
        self.player_rect = player_rect
        
        # Store previous angle to detect swinging
        self.prev_angle = self.angle
        
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
        
        # Detect swinging motion (rapid angle change or left click)
        angle_diff = abs(self.angle - self.prev_angle)
        if angle_diff > math.pi:  # Handle angle wrap-around
            angle_diff = 2 * math.pi - angle_diff
            
        self.is_swinging = left_click or angle_diff > 0.1 or abs(player_vel.x) > 2 or abs(player_vel.y) > 2
        
    def reset(self):
        """Reset staff state"""
        self.angle = 0
        self.prev_angle = 0
        self.is_swinging = False
        
    def draw(self, screen, camera):
        """Draw the staff at the player's position"""
        if not self.player_rect:
            return
        
        # Position staff with a slight offset towards the cursor
        staff_x = self.player_rect.centerx + math.cos(self.angle) * STAFF_OFFSET
        staff_y = self.player_rect.centery + math.sin(self.angle) * STAFF_OFFSET
        
        # Apply camera transform to get screen position
        screen_pos = camera.apply_point((staff_x, staff_y))
        
        # Determine if we need to flip the image and add rotation offset
        is_flipped = False
        rotation_offset = 0
        angle_degrees = math.degrees(self.angle)
        
        if abs(angle_degrees) < 90:  # Right side
            is_flipped = True
            rotation_offset = STAFF_TILT_ANGLE  # Use setting for right side
        else:  # Left side
            rotation_offset = -STAFF_TILT_ANGLE  # Use setting for left side

        # Rotate staff image to point toward mouse with additional offset
        image_to_rotate = pygame.transform.flip(self.image, is_flipped, False)
        rotated_staff = pygame.transform.rotate(image_to_rotate, -angle_degrees - 90 + rotation_offset)
        staff_rect = rotated_staff.get_rect(center=screen_pos)
        
        # Draw the staff
        screen.blit(rotated_staff, staff_rect)