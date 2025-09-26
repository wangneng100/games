import pygame
import math

class Staff:
    def __init__(self, image, color):
        self.image = image
        self.color = color
        self.angle = 0
        self.length = 100
        self.player_rect = None
        
    def update(self, player_rect, left_click, platforms, camera, player_vel):
        """Update staff position and rotation based on mouse position"""
        self.player_rect = player_rect
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Get world mouse position (accounting for camera)
        world_mouse_x = mouse_pos[0] - camera.camera.x
        world_mouse_y = mouse_pos[1] - camera.camera.y
        
        # Calculate angle from player to mouse
        dx = world_mouse_x - player_rect.centerx
        dy = world_mouse_y - player_rect.centery
        self.angle = math.atan2(dy, dx)
        
    def reset(self):
        """Reset staff state"""
        self.angle = 0
        
    def draw(self, screen, camera):
        """Draw the staff at the player's position"""
        if not self.player_rect:
            return
        
        # Position staff directly at player center
        staff_x = self.player_rect.centerx
        staff_y = self.player_rect.centery
        
        # Apply camera transform to get screen position
        screen_pos = camera.apply_point((staff_x, staff_y))
        
        # Determine if we need to flip the image and add rotation offset
        is_flipped = False
        rotation_offset = 0
        angle_degrees = math.degrees(self.angle)
        
        if abs(angle_degrees) < 90:  # Right side
            is_flipped = True
            rotation_offset = 45  # 45 degrees right
        else:  # Left side
            rotation_offset = -45  # 45 degrees left

        # Rotate staff image to point toward mouse with additional offset
        image_to_rotate = pygame.transform.flip(self.image, is_flipped, False)
        rotated_staff = pygame.transform.rotate(image_to_rotate, -angle_degrees - 90 + rotation_offset)
        staff_rect = rotated_staff.get_rect(center=screen_pos)
        
        # Draw the staff
        screen.blit(rotated_staff, staff_rect)