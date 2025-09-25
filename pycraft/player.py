import pygame
import math
from settings import *

class Player:
    """Represents the player character."""
    def __init__(self, x, y, image, staff):
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.acc_x = 0
        self.on_ground = False
        self.angle = 0
        self.jumps_left = 2
        self.staff = staff
        self.spawn_x = x
        self.spawn_y = y

    def reset(self):
        self.rect.topleft = (self.spawn_x, self.spawn_y)
        self.vel_x = 0
        self.vel_y = 0
        self.angle = 0
        self.on_ground = False
        self.jumps_left = 2
        self.staff.reset()

    def update(self, platforms, jump_pressed, left_click, camera, jump_key_released):
        """Handles player movement, gravity, and collision."""

        # --- Get Keyboard Input ---
        keys = pygame.key.get_pressed()
        
        self.acc_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.acc_x = -PLAYER_ACC
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.acc_x = PLAYER_ACC

        # --- Horizontal Movement Physics ---
        # Apply friction
        if self.on_ground:
            self.acc_x += self.vel_x * GROUND_FRICTION
        else:
            self.acc_x += self.vel_x * AIR_FRICTION
            
        # Update velocity
        self.vel_x += self.acc_x

        # Limit velocity
        if abs(self.vel_x) < 0.1:
            self.vel_x = 0
        if self.vel_x > PLAYER_MAX_SPEED:
            self.vel_x = PLAYER_MAX_SPEED
        if self.vel_x < -PLAYER_MAX_SPEED:
            self.vel_x = -PLAYER_MAX_SPEED

        # --- Vertical Movement (Gravity) ---
        if jump_pressed and self.jumps_left > 0:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            self.jumps_left -= 1
        
        if jump_key_released:
            if self.vel_y < 0:
                self.vel_y *= 0.5
            
        self.vel_y += GRAVITY

        if self.vel_y > 10:  # Terminal velocity
            self.vel_y = 10
            
        dx = self.vel_x
        dy = self.vel_y

        # --- Collision Detection ---
        self.on_ground = False
        # Move horizontally and check for collisions
        self.rect.x += int(dx)
        for platform in platforms:
            if self.rect.colliderect(platform):
                if dx > 0:  # Moving right
                    self.rect.right = platform.left
                    self.vel_x = 0
                elif dx < 0:  # Moving left
                    self.rect.left = platform.right
                    self.vel_x = 0

        # Move vertically and check for collisions
        self.rect.y += int(dy) # Using int() for dy
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:  # Moving down
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.angle = 0
                    self.jumps_left = 2
                    self.staff.reset()
                elif self.vel_y < 0:  # Moving up
                    self.rect.top = platform.bottom
                    self.vel_y = 0
        
        target_angle = 0
        if not self.on_ground:
            target_angle = self.vel_x * 3
        
        diff = (target_angle - self.angle + 180) % 360 - 180
        self.angle += diff * 0.1
        
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()



        player_vel = pygame.math.Vector2(self.vel_x, self.vel_y)
        self.staff.update(self.rect, left_click, platforms, camera, player_vel)



    def draw(self, screen, camera):
        """Draws the player on the screen."""


        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        new_rect = rotated_image.get_rect(center = self.rect.center)
        screen.blit(rotated_image, camera.apply(new_rect))
        self.staff.draw(screen, camera)
