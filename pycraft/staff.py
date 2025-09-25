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
        
        # Calculate staff position relative to player
        staff_offset = 40  # Distance from player center
        staff_x = self.player_rect.centerx + math.cos(self.angle) * staff_offset
        staff_y = self.player_rect.centery + math.sin(self.angle) * staff_offset
        
        # Apply camera transform to get screen position
        screen_pos = camera.apply_point((staff_x, staff_y))
        
        # Determine if we need to flip the image
        is_flipped = False
        if abs(math.degrees(self.angle)) < 90:
            is_flipped = True

        # Rotate staff image to point toward mouse
        image_to_rotate = pygame.transform.flip(self.image, is_flipped, False)
        rotated_staff = pygame.transform.rotate(image_to_rotate, -math.degrees(self.angle) - 90)
        staff_rect = rotated_staff.get_rect(center=screen_pos)
        
        # Draw the staff
        screen.blit(rotated_staff, staff_rect)