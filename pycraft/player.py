import pygame
import math
import time
from settings import *
from hotbar import Hotbar
from trail import Trail

class Player:
    """Represents the player character."""
    def __init__(self, x, y, image, bow, knife):
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.acc_x = 0
        self.on_ground = False
        self.angle = 0
        self.jumps_left = 2
        self.bow = bow
        self.knife = knife
        # Initialize arrow list for tracking
        self.arrows = []
        
        # Initialize health tank
        from health_tank import HealthTank
        self.health_tank = HealthTank(max_health=100)
        self.spawn_x = x
        self.spawn_y = y
        self.right_click_held = False
        self.right_click_released = False
        
        # Damage flash effect
        self.damage_flash_time = 0
        self.is_damage_flashing = False
        
        # Enemy reference for aimbot assist
        self.enemy_target = None
        self.right_click_start_time = 0
        self.charge_time = 0
        
        # Hotbar system
        self.hotbar = Hotbar()
        self.current_weapon = None  # Currently equipped weapon
        
        # Particle system
        from particle import ParticleSystem
        self.particle_system = ParticleSystem()
        
        # Dash system
        self.is_dashing = False
        self.dash_start_time = 0
        self.dash_direction_x = 0
        self.dash_direction_y = 0
        self.dash_cooldown_start = 0
        self.dash_trail = Trail(DASH_TRAIL_COLOR, max_length=DASH_TRAIL_LENGTH)
        self.dash_speed = 0  # Current dash speed
        self.dash_roll_angle = 0  # Roll animation angle
        
        # Flurry Rush system
        self.flurry_rush_active = False
        self.flurry_rush_start_time = 0
        self.flurry_rush_cooldown_start = 0
        self.last_enemy_melee_time = 0  # Track when enemy last did melee attack
        
        # Knockback system with variable speed
        self.knockback_vel_x = 0
        self.knockback_vel_y = 0
        self.knockback_time = 0
        self.is_knocked_back = False
        self.initial_knockback_x = 0
        self.initial_knockback_y = 0

    def reset(self):
        self.rect.topleft = (self.spawn_x, self.spawn_y)
        self.vel_x = 0
        self.vel_y = 0
        self.angle = 0
        self.on_ground = False
        self.jumps_left = 2
        self.bow.reset()
        self.arrows.clear()
        self.right_click_held = False
        self.right_click_released = False
        self.right_click_start_time = 0
        self.charge_time = 0
        self.current_weapon = None
        self.is_dashing = False
        self.dash_start_time = 0
        self.dash_cooldown_start = 0
        self.dash_trail.clear()
        self.dash_speed = 0
        self.dash_roll_angle = 0
        
        # Reset flurry rush
        self.flurry_rush_active = False
        self.flurry_rush_start_time = 0
        self.flurry_rush_cooldown_start = 0
        self.last_enemy_melee_time = 0
        
        # Reset health tank
        self.health_tank.reset()

    def update(self, platforms, jump_pressed, left_click, camera, jump_key_released, right_click, keys_pressed=None, mouse_pos=None, dash_pressed=False):
        """Handles player movement, gravity, and collision."""

        # Get current time at the beginning
        current_time = time.time()
        
        # Handle damage flash effect
        if self.is_damage_flashing:
            self.damage_flash_time -= 1/60  # Assuming 60 FPS
            if self.damage_flash_time <= 0:
                self.is_damage_flashing = False

        # --- Handle hotbar input ---
        if keys_pressed:
            self.hotbar.handle_key_input(keys_pressed)
        
        # Update current weapon based on selected hotbar slot
        selected_item = self.hotbar.get_selected_item()
        if selected_item and hasattr(selected_item, 'weapon'):
            self.current_weapon = selected_item.weapon
        else:
            self.current_weapon = None
            
        # --- Handle dash input ---
        if dash_pressed and not self.is_dashing:
            # Check if dash is off cooldown
            if current_time - self.dash_cooldown_start >= DASH_COOLDOWN:
                # Check for flurry rush trigger (dash during enemy melee attack)
                if (self.enemy_target and 
                    hasattr(self.enemy_target, 'attack_state') and 
                    self.enemy_target.attack_state == 'charging' and
                    current_time - self.flurry_rush_cooldown_start >= FLURRY_RUSH_COOLDOWN):
                    
                    # Trigger flurry rush!
                    self.trigger_flurry_rush(current_time)
                    
                self.start_dash(keys_pressed)
                
        # Update dash state
        if self.is_dashing:
            if current_time - self.dash_start_time >= DASH_DURATION:
                self.is_dashing = False
            else:
                # Add position to dash trail
                self.dash_trail.add_position(self.rect.centerx, self.rect.centery)
                
        # Update flurry rush state
        if self.flurry_rush_active:
            if current_time - self.flurry_rush_start_time >= FLURRY_RUSH_DURATION:
                self.flurry_rush_active = False

        # --- Handle weapon attacks based on current weapon ---
        
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
                arrow = self.bow.shoot_arrow(self.enemy_target)  # Pass enemy for aimbot assist
                if arrow:
                    arrow.particle_system = self.particle_system  # Give arrow access to particle system
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

        # Handle knockback with deceleration
        if self.is_knocked_back:
            self.knockback_time -= 1/60
            # Decelerate knockback velocity
            self.knockback_vel_x *= KNOCKBACK_DECELERATION
            self.knockback_vel_y *= KNOCKBACK_DECELERATION
            
            # Stop when velocity becomes very small or time runs out
            if (abs(self.knockback_vel_x) < 0.1 and abs(self.knockback_vel_y) < 0.1) or self.knockback_time <= 0:
                self.is_knocked_back = False
                self.knockback_vel_x = 0
                self.knockback_vel_y = 0
        
        # --- Horizontal Movement Physics ---
        if self.is_knocked_back:
            # Override with knockback velocity
            self.vel_x = self.knockback_vel_x
            self.vel_y = self.knockback_vel_y
        elif self.is_dashing:
            # Override normal movement with dash velocity (variable speed)
            self.vel_x = self.dash_direction_x * self.dash_speed
            self.vel_y = self.dash_direction_y * self.dash_speed
            # Decelerate dash speed
            self.dash_speed *= DASH_DECELERATION
            # Update roll angle
            self.dash_roll_angle += DASH_ROLL_SPEED
        else:
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

        # --- Optimized Collision Detection ---
        self.on_ground = False
        
        # Move horizontally with basic collision
        self.rect.x += int(dx)
        for platform in platforms:
            if self.rect.colliderect(platform):
                if dx > 0:  # Moving right
                    self.rect.right = platform.left
                    self.vel_x = 0
                elif dx < 0:  # Moving left
                    self.rect.left = platform.right
                    self.vel_x = 0
                break
        
        # Move vertically with basic collision
        self.rect.y += int(dy)
        for platform in platforms:
            if self.rect.colliderect(platform):
                if dy > 0:  # Moving down
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.angle = 0
                    self.jumps_left = 2
                    self.bow.reset()
                elif dy < 0:  # Moving up
                    self.rect.top = platform.bottom
                    self.vel_y = 0
                break
        
        target_angle = 0
        if not self.on_ground:
            target_angle = self.vel_x * 3
        
        diff = (target_angle - self.angle + 180) % 360 - 180
        self.angle += diff * 0.1
        
        if self.rect.top > SCREEN_HEIGHT:
            # Take void damage when falling out of world
            self.take_damage(100, is_void=True)

        # Update current weapon based on hotbar selection
        selected_item = self.hotbar.get_selected_item()
        if selected_item:
            self.current_weapon = selected_item.weapon
        else:
            self.current_weapon = None
        
        # Update bow when equipped
        if self.current_weapon == self.bow:
            self.bow.update(self.rect, True, camera, self.charge_time if self.right_click_held else 0)
        
        # Update knife only when equipped
        if self.current_weapon == self.knife and mouse_pos:
            self.knife.update(self.rect, mouse_pos, left_click, right_click, camera)
        
        # Update arrows
        self.arrows = [arrow for arrow in self.arrows if arrow.alive]
        for arrow in self.arrows:
            arrow.update(platforms)
            
        # Update particle system
        self.particle_system.update()
        
        # Update health tank
        self.health_tank.update()
        
        # Continuous death check
        if self.health_tank.current_health <= 0:
            self.reset()
            
    def start_dash(self, keys_pressed):
        """Start a dash in the direction of movement keys"""
        # Determine dash direction from input
        dash_x = 0
        dash_y = 0
        
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            dash_x = -1
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            dash_x = 1
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            dash_y = -1
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            dash_y = 1
            
        # If no direction keys pressed, dash in the direction player is facing
        if dash_x == 0 and dash_y == 0:
            if self.vel_x > 0:
                dash_x = 1
            elif self.vel_x < 0:
                dash_x = -1
            else:
                dash_x = 1  # Default to right
                
        # Normalize diagonal movement
        if dash_x != 0 and dash_y != 0:
            dash_x *= 0.707  # sqrt(2)/2
            dash_y *= 0.707
            
        self.dash_direction_x = dash_x
        self.dash_direction_y = dash_y
        self.is_dashing = True
        self.dash_start_time = time.time()
        self.dash_cooldown_start = time.time()
        self.dash_trail.clear()  # Clear previous trail
        self.dash_speed = DASH_INITIAL_SPEED  # Set initial dash speed
        self.dash_roll_angle = 0  # Reset roll angle



    def draw(self, screen, camera):
        """Draws the player on the screen."""

        # Apply roll animation during dash
        player_angle = self.angle
        if self.is_dashing:
            player_angle += self.dash_roll_angle
            
        rotated_image = pygame.transform.rotate(self.original_image, player_angle)
        new_rect = rotated_image.get_rect(center = self.rect.center)
        
        # Apply red flash effect when taking damage
        if self.is_damage_flashing:
            # Create red-tinted version
            flash_surface = pygame.Surface(rotated_image.get_size(), pygame.SRCALPHA)
            flash_surface.fill((255, 0, 0, 128))  # Semi-transparent red
            
            # Create flashed image
            flashed_image = rotated_image.copy()
            flashed_image.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_MULT)
            
            screen.blit(flashed_image, camera.apply(new_rect))
        else:
            screen.blit(rotated_image, camera.apply(new_rect))
        
        # Draw current equipped weapon
        if self.current_weapon == self.bow:
            self.bow.draw(screen, camera)
        elif self.current_weapon == self.knife:
            self.knife.draw(screen, camera)
        
        # Draw arrows
        for arrow in self.arrows:
            arrow.draw(screen, camera)
            
        # Draw dash trail
        if self.is_dashing:
            self.dash_trail.draw(screen, camera)
            
        # Draw particles
        self.particle_system.draw(screen, camera)
        
        # Draw health tank (UI element - not affected by camera)
        self.health_tank.draw(screen)
            
    def handle_hotbar_click(self, mouse_pos):
        """Handle mouse clicks on hotbar"""
        return self.hotbar.handle_mouse_click(mouse_pos)
    
    def handle_hotbar_scroll(self, scroll_direction):
        """Handle mouse wheel scrolling for hotbar"""
        return self.hotbar.handle_scroll(scroll_direction)
        
    def apply_knockback(self, force_x, force_y, duration_multiplier=1.0):
        """Apply knockback to the player with variable force and duration"""
        self.knockback_vel_x = force_x
        self.knockback_vel_y = force_y
        self.initial_knockback_x = force_x
        self.initial_knockback_y = force_y
        
        # Duration based on force strength
        force_magnitude = math.sqrt(force_x*force_x + force_y*force_y)
        duration = KNOCKBACK_MIN_DURATION + (force_magnitude / 20.0) * (KNOCKBACK_MAX_DURATION - KNOCKBACK_MIN_DURATION)
        self.knockback_time = duration * duration_multiplier
        self.is_knocked_back = True
        

                
    def check_enemy_collision(self, enemy):
        """No collision effects - player and enemy can overlap freely"""
        # Player can move through enemy completely
        # No pushing, no stopping, no collision effects at all
        # Only the sword system can affect the enemy
        pass

                
    def check_arrow_hits(self, enemy):
        """Check if arrows hit the enemy with smaller hitbox"""
        for arrow in self.arrows[:]:
            if arrow.alive:
                # Create smaller hitbox for arrow
                arrow_hitbox = pygame.Rect(
                    arrow.rect.centerx - ARROW_HITBOX_SIZE//2,
                    arrow.rect.centery - ARROW_HITBOX_SIZE//2,
                    ARROW_HITBOX_SIZE,
                    ARROW_HITBOX_SIZE
                )
                
                if arrow_hitbox.colliderect(enemy.rect):
                    # Create particle explosion on enemy hit
                    self.particle_system.create_explosion(
                        arrow.rect.centerx, arrow.rect.centery,
                        ARROW_PARTICLE_COLOR, count=PARTICLE_COUNT
                    )
                    
                    # Calculate arrow speed and impact force
                    arrow_speed = math.sqrt(arrow.vel_x*arrow.vel_x + arrow.vel_y*arrow.vel_y)
                    speed_ratio = max(arrow_speed / ARROW_BASE_SPEED, 0.5)  # Minimum 50% force for close shots
                    
                    # Reduce force if arrow has pierced blocks
                    pierce_reduction = 1.0 - (arrow.blocks_pierced * 0.3)
                    
                    # Calculate realistic knockback based on arrow momentum
                    force = BASE_KNOCKBACK_FORCE * ARROW_KNOCKBACK_MULTIPLIER * speed_ratio * pierce_reduction
                    dx = math.cos(arrow.angle) * force
                    dy = math.sin(arrow.angle) * force * 0.2  # Less vertical knockback
                    
                    # Apply knockback to enemy (works even if already knocked back)
                    enemy.apply_knockback(dx, dy, 0.8)
                    
                    # Damage enemy based on arrow charge power (100x weaker than original)
                    base_damage = 0.15  # Base damage (was 1.5, originally 15)
                    charge_bonus = 0.35 * arrow.charge_power  # 0-0.35 bonus damage based on charge (was 0-3.5, originally 0-35)
                    total_damage = (base_damage + charge_bonus) * self.get_damage_multiplier()  # Apply flurry rush multiplier
                    enemy.take_damage(total_damage)
                    
                    # Heal player for hitting enemy
                    self.heal(10)  # Gain 10 HP per arrow hit
                    print(f"Arrow hit! +10 HP. Health: {self.health_tank.current_health}")
                    
                    # Remove arrow
                    arrow.alive = False
        
        # Clean up dead arrows
        self.arrows = [arrow for arrow in self.arrows if arrow.alive]
    
    def check_knife_hit(self, enemy):
        """Check if knife stab hits enemy"""
        if self.knife.check_attack_hit(enemy.rect):
            # Calculate knockback direction from knife angle
            dx = math.cos(self.knife.angle)
            dy = math.sin(self.knife.angle) * 0.3  # Less vertical knockback
            
            # Apply knockback with attack strength (1.0 for left click, 2.0 for right click)
            force = BASE_KNOCKBACK_FORCE * KNIFE_DAMAGE_MULTIPLIER * self.knife.attack_strength
            enemy.apply_knockback(dx * force, dy * force, 0.6)
            
            # Damage enemy (100x weaker)
            knife_damage = 0.15 * self.knife.attack_strength * self.get_damage_multiplier()  # Apply flurry rush multiplier
            enemy.take_damage(knife_damage)
            
            # Heal player for hitting enemy
            self.heal(1)  # Gain 1 HP per knife hit
            print(f"Knife hit! +1 HP. Health: {self.health_tank.current_health}")
            
            return True
        return False
    
    def take_damage(self, damage, is_void=False):
        """Take damage and update health tank"""
        self.health_tank.take_damage(damage, is_void)
        
        # Trigger damage flash effect
        self.damage_flash_time = 0.3  # Flash for 0.3 seconds
        self.is_damage_flashing = True
        
        # Always check if dead after taking damage
        if self.health_tank.current_health <= 0:
            self.reset()  # Reset player when dead
    
    def trigger_flurry_rush(self, current_time):
        """Trigger flurry rush mode with bullet time and enhanced damage"""
        self.flurry_rush_active = True
        self.flurry_rush_start_time = current_time
        self.flurry_rush_cooldown_start = current_time
        print("FLURRY RUSH ACTIVATED! 10x damage for 3 seconds!")
    
    def get_damage_multiplier(self):
        """Get current damage multiplier (10x during flurry rush)"""
        if self.flurry_rush_active:
            return FLURRY_RUSH_DAMAGE_MULTIPLIER
        return 1.0
    
    def heal(self, amount):
        """Heal player"""
        self.health_tank.heal(amount)
    
    def draw_hotbar(self, screen):
        """Draw the hotbar UI"""
        self.hotbar.draw(screen)
