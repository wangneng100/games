import pygame
import math
import time
from settings import *
from hotbar import Hotbar

class Player:
    """Represents the player character."""
    def __init__(self, x, y, image, staff, bow):
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
        self.bow = bow
        self.arrows = []  # List to store active arrows
        self.spawn_x = x
        self.spawn_y = y
        self.right_click_held = False
        self.right_click_released = False
        self.right_click_start_time = 0
        self.charge_time = 0
        
        # Hotbar system
        self.hotbar = Hotbar()
        self.current_weapon = None  # Currently equipped weapon

    def reset(self):
        self.rect.topleft = (self.spawn_x, self.spawn_y)
        self.vel_x = 0
        self.vel_y = 0
        self.angle = 0
        self.on_ground = False
        self.jumps_left = 2
        self.staff.reset()
        self.bow.reset()
        self.arrows.clear()
        self.right_click_held = False
        self.right_click_released = False
        self.right_click_start_time = 0
        self.charge_time = 0
        self.current_weapon = None

    def update(self, platforms, jump_pressed, left_click, camera, jump_key_released, right_click, keys_pressed=None, mouse_pos=None):
        """Handles player movement, gravity, and collision."""

        # --- Handle hotbar input ---
        if keys_pressed:
            self.hotbar.handle_key_input(keys_pressed)
        
        # Update current weapon based on selected hotbar slot
        selected_item = self.hotbar.get_selected_item()
        if selected_item and hasattr(selected_item, 'weapon'):
            self.current_weapon = selected_item.weapon
        else:
            self.current_weapon = None

        # --- Handle weapon attacks based on current weapon ---
        current_time = time.time()
        
        # Only handle bow mechanics when bow is equipped
        if self.current_weapon == self.bow:
            if right_click and not self.right_click_held:
                # Just started holding right click
                self.right_click_held = True
                self.right_click_released = False
                self.right_click_start_time = current_time
                self.charge_time = 0
            elif right_click and self.right_click_held:
                # Continue holding right click - update charge time
                self.charge_time = current_time - self.right_click_start_time
                self.right_click_released = False
            elif not right_click and self.right_click_held:
                # Just released right click - shoot arrow
                self.right_click_held = False
                self.right_click_released = True
                arrow = self.bow.shoot_arrow()
                if arrow:
                    self.arrows.append(arrow)
                self.charge_time = 0
            else:
                self.right_click_released = False
                self.charge_time = 0
        else:
            # Reset bow states when not equipped
            self.right_click_held = False
            self.right_click_released = False
            self.charge_time = 0

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
                    self.bow.reset()
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

        # Update current weapon based on what's equipped
        if self.current_weapon == self.bow:
            # Update bow when bow is equipped (always show, charge when right click held)
            self.bow.update(self.rect, True, camera, self.charge_time if self.right_click_held else 0)
        elif self.current_weapon == self.staff:
            # Update staff when staff is equipped
            player_vel = pygame.math.Vector2(self.vel_x, self.vel_y)
            self.staff.update(self.rect, left_click, platforms, camera, player_vel)
        
        # Update arrows
        self.arrows = [arrow for arrow in self.arrows if arrow.alive]
        for arrow in self.arrows:
            arrow.update(platforms)



    def draw(self, screen, camera):
        """Draws the player on the screen."""

        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        new_rect = rotated_image.get_rect(center = self.rect.center)
        screen.blit(rotated_image, camera.apply(new_rect))
        
        # Draw current weapon based on what's equipped
        if self.current_weapon == self.bow:
            # Draw bow when equipped (always visible)
            self.bow.draw(screen, camera)
        elif self.current_weapon == self.staff:
            # Draw staff when equipped
            self.staff.draw(screen, camera)
        
        # Draw arrows
        for arrow in self.arrows:
            arrow.draw(screen, camera)
            
    def handle_hotbar_click(self, mouse_pos):
        """Handle mouse clicks on hotbar"""
        return self.hotbar.handle_mouse_click(mouse_pos)
        
    def draw_hotbar(self, screen):
        """Draw the hotbar UI"""
        self.hotbar.draw(screen)
