import pygame
import math
from settings import *

class Knife:
    """A small, quick knife that follows the mouse and stabs on click"""
    
    def __init__(self, image, avg_color):
        self.original_image = image
        self.image = image
        self.avg_color = avg_color
        self.angle = 0
        self.visible = True
        self.attack_active = False
        self.attack_time = 0
        self.attack_cooldown = 0
        self.stab_phase = None  # 'forward' or 'return'
        self.base_angle = 0  # Base angle before attack
        self.last_left_click = False
        self.last_right_click = False
        self.attack_strength = 1.0  # 1.0 for left click, 2.0 for right click
        
        # Make knife very small
        knife_size = (int(image.get_width() * KNIFE_SCALE), 
                     int(image.get_height() * KNIFE_SCALE))
        self.image = pygame.transform.scale(self.original_image, knife_size)
        self.original_scaled = self.image.copy()
        
        # Position tracking
        self.rect = self.image.get_rect()
        
    def update(self, player_rect, mouse_pos, left_click, right_click, camera):
        """Update knife position and attack mechanics"""
        import random
        
        # Convert mouse position to world coordinates
        world_mouse_x = mouse_pos[0] - camera.camera.x
        world_mouse_y = mouse_pos[1] - camera.camera.y
        
        # Calculate base angle from player to mouse
        dx = world_mouse_x - player_rect.centerx
        dy = world_mouse_y - player_rect.centery
        
        if dx != 0 or dy != 0:
            self.base_angle = math.atan2(dy, dx)
        
        # Set current angle (always points to mouse)
        self.angle = self.base_angle
        
        # Position knife with stab animation
        offset_distance = KNIFE_OFFSET
        if self.attack_active:
            # Calculate total progress (0 = start, 1 = end)
            total_progress = 1.0 - (self.attack_time / KNIFE_STAB_DURATION)
            
            # Determine phase and calculate extension with attack strength
            forward_duration = KNIFE_STAB_DURATION * KNIFE_STAB_FORWARD_RATIO
            max_extension = KNIFE_STAB_EXTENSION * self.attack_strength  # 2x extension for right click
            
            if self.attack_time > (KNIFE_STAB_DURATION - forward_duration):
                # Forward phase - quick stab out
                self.stab_phase = 'forward'
                phase_progress = 1.0 - ((self.attack_time - (KNIFE_STAB_DURATION - forward_duration)) / forward_duration)
                extension = max_extension * phase_progress
            else:
                # Return phase - slow pull back
                self.stab_phase = 'return'
                return_duration = KNIFE_STAB_DURATION * KNIFE_STAB_RETURN_RATIO
                phase_progress = 1.0 - (self.attack_time / return_duration)
                extension = max_extension * (1.0 - phase_progress)
            
            offset_distance += extension
            
        self.rect.centerx = player_rect.centerx + math.cos(self.angle) * offset_distance
        self.rect.centery = player_rect.centery + math.sin(self.angle) * offset_distance
        
        # Handle attack timing
        if self.attack_active:
            self.attack_time -= 1/60
            if self.attack_time <= 0:
                self.attack_active = False
                self.stab_phase = None
        
        # Handle attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1/60
        
        # Detect new clicks to start attack
        new_left_click = left_click and not self.last_left_click
        new_right_click = right_click and not self.last_right_click
        
        if (new_left_click or new_right_click) and self.attack_cooldown <= 0:
            # Determine attack strength based on which button was pressed
            if new_right_click:
                self.start_attack(strength=KNIFE_RIGHT_CLICK_MULTIPLIER)
            else:
                self.start_attack(strength=1.0)
        
        self.last_left_click = left_click
        self.last_right_click = right_click
        
        # Determine if knife should be flipped based on mouse position
        should_flip = world_mouse_x < player_rect.centerx
        
        # Flip the image if needed (flip vertically for correct orientation)
        knife_image = self.original_scaled
        if should_flip:
            knife_image = pygame.transform.flip(self.original_scaled, False, True)
        
        # Rotate image to face current angle
        angle_degrees = math.degrees(self.angle)
        self.image = pygame.transform.rotate(knife_image, -angle_degrees)
        self.rect = self.image.get_rect(center=self.rect.center)
    
    def start_attack(self, strength=1.0):
        """Start a stab attack with quick forward, slow return"""
        self.attack_active = True
        self.attack_time = KNIFE_STAB_DURATION
        self.stab_phase = 'forward'
        self.attack_cooldown = KNIFE_ATTACK_COOLDOWN
        self.attack_strength = strength
    
    def draw(self, screen, camera):
        """Draw the knife"""
        if self.visible:
            screen.blit(self.image, camera.apply(self.rect))
    
    def check_attack_hit(self, enemy_rect):
        """Check if knife stab hits enemy during forward phase"""
        if not self.attack_active:
            return False
            
        # Only hit during forward phase of stab
        if self.stab_phase == 'forward':
            return self._check_hitbox(enemy_rect)
        
        return False
    
    def _check_hitbox(self, enemy_rect):
        """Helper method to check hitbox collision"""
        # Create small hitbox at knife tip
        tip_x = self.rect.centerx + math.cos(self.angle) * (self.rect.width // 2)
        tip_y = self.rect.centery + math.sin(self.angle) * (self.rect.height // 2)
        
        knife_hitbox = pygame.Rect(
            tip_x - KNIFE_HITBOX_SIZE // 2,
            tip_y - KNIFE_HITBOX_SIZE // 2,
            KNIFE_HITBOX_SIZE,
            KNIFE_HITBOX_SIZE
        )
        
        return knife_hitbox.colliderect(enemy_rect)
    
    def reset(self):
        """Reset knife state"""
        self.attack_active = False
        self.attack_time = 0
        self.attack_cooldown = 0
        self.stab_phase = None
        self.last_left_click = False
        self.last_right_click = False
        self.attack_strength = 1.0