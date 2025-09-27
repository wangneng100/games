import pygame
import random
import math
from settings import *

class Enemy:
    """Simple enemy for testing - can't die, moves and jumps"""
    def __init__(self, x, y, image):
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.acc_x = 0
        self.on_ground = False
        self.angle = 0
        self.jumps_left = 2
        self.spawn_x = x
        self.spawn_y = y
        
        # AI behavior
        self.move_direction = random.choice([-1, 1])  # -1 for left, 1 for right
        self.move_timer = 0
        self.jump_timer = 0
        self.direction_change_time = random.uniform(2.0, 5.0)  # Change direction every 2-5 seconds
        self.jump_chance_time = random.uniform(1.0, 3.0)  # Try to jump every 1-3 seconds
        
        # Knockback system with variable speed
        self.knockback_vel_x = 0
        self.knockback_vel_y = 0
        self.knockback_time = 0
        self.is_knocked_back = False
        self.initial_knockback_x = 0
        self.initial_knockback_y = 0
        
        # Hit flash effect
        self.hit_flash_time = 0
        self.is_flashing = False
        
        # Attack system
        self.attack_cooldown = 0
        self.can_attack = True
        
        # Enemy spinning cross attack system
        self.attack_state = 'idle'  # 'idle', 'charging'
        self.attack_timer = 0
        self.cross_size = 0
        self.max_cross_size = 120  # Starting size for cross
        self.min_cross_size = 25   # Minimum size before dealing damage
        self.attack_center_x = 0
        self.attack_center_y = 0
        self.cross_rotation = 0  # Current rotation angle in degrees
        self.has_dealt_damage = False  # Track if we've dealt damage this attack
        self.particle_system = None  # Will be set by main.py
        
        # Lightning attack system
        self.lightning_cooldown = 0
        self.can_lightning_attack = True
        self.lightning_attack_range = 400  # Range for lightning attacks
        self.lightning_state = 'idle'  # 'idle', 'warning', 'striking'
        self.lightning_timer = 0
        self.lightning_target_x = 0
        self.lightning_target_y = 0
        self.has_lightning_damaged = False
        
        # Evasion and mobility system
        self.dash_cooldown = 0
        self.can_dash = True
        self.is_dashing = False
        self.dash_duration = 0
        
        # Enhanced dodging system
        self.dodge_cooldown = 0
        self.can_dodge = True
        self.dodge_timer = 0
        self.is_dodging = False
        self.dodge_direction_x = 0
        self.dash_speed = 800  # Dash speed
        self.dash_direction = 0
        self.evasion_timer = 0
        self.arrow_detection_range = 200  # How far to detect incoming arrows
        
        # Boss health system
        self.max_health = 500  # Boss has 500 HP
        self.current_health = self.max_health
        self.health_flash_time = 0  # Flash when taking damage
        self.is_health_flashing = False
        
    def update(self, platforms, player):
        """Update enemy AI and physics"""
        import time
        current_time = time.time()
        
        # Handle knockback with deceleration
        if self.is_knocked_back:
            self.knockback_time -= 1/60
            # Decelerate horizontal knockback velocity only
            self.knockback_vel_x *= KNOCKBACK_DECELERATION
            # Let vertical knockback decay naturally with gravity instead of forced deceleration
            
            # Stop when horizontal velocity becomes small or time runs out
            if abs(self.knockback_vel_x) < 0.1 or self.knockback_time <= 0:
                self.is_knocked_back = False
                self.knockback_vel_x = 0
                
        # Handle hit flash effect
        if self.is_flashing:
            self.hit_flash_time -= 1/60
            if self.hit_flash_time <= 0:
                self.is_flashing = False
        
        # Handle health flash effect
        if self.is_health_flashing:
            self.health_flash_time -= 1/60
            if self.health_flash_time <= 0:
                self.is_health_flashing = False
        
        # Handle attack cooldown
        if not self.can_attack:
            self.attack_cooldown -= 1/60
            if self.attack_cooldown <= 0:
                self.can_attack = True
        
        # Handle lightning cooldown
        if not self.can_lightning_attack:
            self.lightning_cooldown -= 1/60
            if self.lightning_cooldown <= 0:
                self.can_lightning_attack = True
        
        # Handle dodge cooldown
        if not self.can_dodge:
            self.dodge_cooldown -= 1/60
            if self.dodge_cooldown <= 0:
                self.can_dodge = True
        
        # Handle dodge duration
        if self.is_dodging:
            self.dodge_timer -= 1/60
            if self.dodge_timer <= 0:
                self.is_dodging = False
        
        # Handle lightning attack states
        if self.lightning_state != 'idle':
            self.lightning_timer -= 1/60
            
            if self.lightning_state == 'warning':
                # Red warning flash phase
                if self.lightning_timer <= 0:
                    self.lightning_state = 'striking'
                    self.lightning_timer = 0.3  # Lightning strike duration
                    
            elif self.lightning_state == 'striking':
                # Blue lightning strike phase
                if self.lightning_timer <= 0:
                    self.lightning_state = 'idle'
        
        # Handle spinning cross attack states
        if self.attack_state != 'idle':
            self.attack_timer -= 1/60
            
            if self.attack_state == 'charging':
                # Cross stays at initial spawn position (doesn't follow player)
                
                # Spinning cross phase - rotates and shrinks every degree
                rotation_speed = 540  # degrees per second (1.5 full rotations/sec)
                self.cross_rotation += rotation_speed * (1/60)  # Add rotation each frame
                
                # Shrink cross size based on total rotation (every degree makes it smaller)
                total_rotation = self.cross_rotation
                shrink_per_degree = (self.max_cross_size - self.min_cross_size) / 360  # Shrink over 360 degrees
                self.cross_size = max(self.min_cross_size, self.max_cross_size - (total_rotation * shrink_per_degree))
                
                # Damage checking is handled by check_circle_hit method called from main.py
                
                # End attack after enough rotation
                if total_rotation >= 360:  # One full rotation
                    # Create damaging particle explosion at cross center
                    if hasattr(self, 'particle_system') and self.particle_system:
                        self.particle_system.create_explosion(
                            self.attack_center_x, self.attack_center_y, 
                            (255, 0, 0), count=15, can_damage=True, damage=5  # Damaging red particles
                        )
                    self.attack_state = 'idle'
                    self.cross_size = 0
                    self.cross_rotation = 0
        
        # Handle dash cooldown and duration
        if not self.can_dash:
            self.dash_cooldown -= 1/60
            if self.dash_cooldown <= 0:
                self.can_dash = True
        
        if self.is_dashing:
            self.dash_duration -= 1/60
            if self.dash_duration <= 0:
                self.is_dashing = False
                self.vel_x *= 0.3  # Slow down after dash
        
        # Detect incoming arrows and try to evade
        if not self.is_knocked_back and not self.is_dashing:
            for arrow in player.arrows if hasattr(player, 'arrows') else []:
                if hasattr(arrow, 'alive') and arrow.alive:
                    # Calculate arrow trajectory and predict if it will hit
                    arrow_to_enemy_x = self.rect.centerx - arrow.rect.centerx
                    arrow_to_enemy_y = self.rect.centery - arrow.rect.centery
                    arrow_distance = math.sqrt(arrow_to_enemy_x**2 + arrow_to_enemy_y**2)
                    
                    if arrow_distance < self.arrow_detection_range:
                        # Calculate if arrow is heading towards us
                        arrow_vel_mag = math.sqrt(arrow.vel_x**2 + arrow.vel_y**2)
                        if arrow_vel_mag > 0:
                            # Normalize arrow velocity
                            arrow_dir_x = arrow.vel_x / arrow_vel_mag
                            arrow_dir_y = arrow.vel_y / arrow_vel_mag
                            
                            # Check if arrow is roughly aimed at enemy
                            to_enemy_normalized_x = arrow_to_enemy_x / max(arrow_distance, 1)
                            to_enemy_normalized_y = arrow_to_enemy_y / max(arrow_distance, 1)
                            
                            dot_product = arrow_dir_x * to_enemy_normalized_x + arrow_dir_y * to_enemy_normalized_y
                            
                            # Enhanced dodging - more aggressive when player is NOT in flurry rush
                            dodge_threshold = 0.4 if not player.flurry_rush_active else 0.8  # Much more sensitive dodging during normal combat
                            
                            if dot_product > dodge_threshold and self.can_dash:
                                # Chance-based dodging for normal attacks to make them hard to land
                                if not player.flurry_rush_active and random.random() < ENEMY_DODGE_CHANCE:
                                    self.start_evasion_dash(arrow)
                                    break
                                elif player.flurry_rush_active:
                                    # Still dodge during flurry rush but less frequently
                                    self.start_evasion_dash(arrow)
                                    break
        
        # AI: Follow player when not knocked back or dashing
        if not self.is_knocked_back and not self.is_dashing:
            # Calculate distance to player
            distance_to_player = math.sqrt(
                (player.rect.centerx - self.rect.centerx)**2 + 
                (player.rect.centery - self.rect.centery)**2
            )
            
            # Aggressive predictive dodging when player is NOT in flurry rush
            if (not player.flurry_rush_active and 
                distance_to_player <= ENEMY_DODGE_DETECTION_RANGE and
                self.can_dodge and
                hasattr(player, 'bow') and player.bow.is_charging):
                
                # Randomly dodge when player is charging bow (makes normal attacks hard to land)
                if random.random() < ENEMY_DODGE_CHANCE:
                    self.start_predictive_dodge(player)
            
            # Choose attack based on distance
            if distance_to_player <= ENEMY_ATTACK_RANGE and self.can_attack and self.attack_state == 'idle':
                # Close range - use cross attack
                self.start_circle_attack(player.rect)
            elif distance_to_player <= self.lightning_attack_range and self.can_lightning_attack and self.lightning_state == 'idle':
                # Medium range - use lightning attack
                self.start_lightning_attack(player.rect)
            
            # Follow player even during attacks (keep moving)
            if distance_to_player > 30:  # Reduced distance so enemy keeps moving
                if player.rect.centerx > self.rect.centerx:
                    self.move_direction = 1  # Move right toward player
                else:
                    self.move_direction = -1  # Move left toward player
            else:
                # Keep moving slowly even when close during attacks
                if self.attack_state == 'charging':
                    if player.rect.centerx > self.rect.centerx:
                        self.move_direction = 0.3  # Slow movement during attack
                    else:
                        self.move_direction = -0.3
                else:
                    self.move_direction = 0  # Only stop when not attacking
        
        self.move_timer += 1/60  # Assuming 60 FPS
        self.jump_timer += 1/60
            
        # Try to jump occasionally
        jump_pressed = False
        if self.jump_timer >= self.jump_chance_time and self.on_ground:
            if random.random() < 0.3:  # 30% chance to jump
                jump_pressed = True
            self.jump_timer = 0
            self.jump_chance_time = random.uniform(1.0, 3.0)
            
        # Apply movement (including knockback and dash)
        if self.is_knocked_back:
            self.acc_x = 0  # No control during knockback
            # Apply knockback with ground friction for more realistic physics
            if self.on_ground:
                self.knockback_vel_x *= 0.92  # Ground friction slows down knockback
            else:
                self.knockback_vel_x *= 0.98  # Less air resistance
            self.vel_x = self.knockback_vel_x
            # Don't override vel_y with knockback_vel_y - let gravity work naturally
        elif self.is_dashing:
            # Dash movement overrides normal movement
            self.vel_x = self.dash_direction * self.dash_speed * (1/60)
            self.acc_x = 0
        elif self.is_dodging:
            # Dodge movement overrides normal movement
            self.vel_x = self.dodge_direction_x * ENEMY_DODGE_SPEED
            self.acc_x = 0
        else:
            self.acc_x = self.move_direction * PLAYER_ACC * 0.7  # Slightly slower than player
        
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
        max_speed = PLAYER_MAX_SPEED * 0.8  # Slightly slower than player
        if self.vel_x > max_speed:
            self.vel_x = max_speed
        if self.vel_x < -max_speed:
            self.vel_x = -max_speed
            
        # Jumping
        if jump_pressed and self.jumps_left > 0:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            self.jumps_left -= 1
            
        # Gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:  # Terminal velocity
            self.vel_y = 10
            
        # Simplified movement and collision for better performance
        dx = self.vel_x
        dy = self.vel_y
        
        # Basic collision detection
        self.on_ground = False
        
        # Move horizontally with improved collision
        old_x = self.rect.x
        self.rect.x += int(dx)
        
        for platform in platforms:
            if self.rect.colliderect(platform):
                if dx > 0:  # Moving right
                    self.rect.right = platform.left
                    self.vel_x = 0
                    self.move_direction *= -1  # Reverse direction when hitting wall
                elif dx < 0:  # Moving left
                    self.rect.left = platform.right
                    self.vel_x = 0
                    self.move_direction *= -1  # Reverse direction when hitting wall
                break
        
        # Move vertically with improved collision
        old_y = self.rect.y
        self.rect.y += int(dy)
        
        for platform in platforms:
            if self.rect.colliderect(platform):
                if dy > 0:  # Moving down
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.angle = 0
                    self.jumps_left = 2
                elif dy < 0:  # Moving up
                    self.rect.top = platform.bottom
                    self.vel_y = 0
                break
                    
        # Smoother rotation based on movement
        target_angle = 0
        if not self.on_ground:
            target_angle = self.vel_x * 2  # Reduced rotation for smoother look
            
        diff = (target_angle - self.angle + 180) % 360 - 180
        self.angle += diff * 0.08  # Smoother angle interpolation
        
        # Prevent enemy from going too far off screen or getting stuck
        if self.rect.top > SCREEN_HEIGHT + 100:  # Reset sooner
            self.rect.topleft = (self.spawn_x, self.spawn_y)
            self.vel_x = 0
            self.vel_y = 0
            self.angle = 0
            self.is_knocked_back = False
            self.knockback_vel_x = 0
            self.knockback_vel_y = 0
        
        # Prevent enemy from getting stuck in walls or going too far horizontally
        if self.rect.left < -50 or self.rect.right > SCREEN_WIDTH + 50:
            # Gently push back toward spawn area
            if self.rect.centerx < self.spawn_x:
                self.move_direction = 1
            else:
                self.move_direction = -1
            
    def can_attack_player(self, player_rect):
        """Check if enemy can attack the player (within range and cooldown ready)"""
        if not self.can_attack:
            return False
            
        distance = math.sqrt(
            (self.rect.centerx - player_rect.centerx)**2 + 
            (self.rect.centery - player_rect.centery)**2
        )
        return distance <= ENEMY_ATTACK_RANGE
    
    def start_circle_attack(self, player_rect):
        """Start a spinning cross attack that follows player position"""
        # Set initial attack center to player's current position
        self.attack_center_x = player_rect.centerx
        self.attack_center_y = player_rect.centery
        
        # Start spinning cross phase
        self.attack_state = 'charging'
        self.attack_timer = 1.0  # Duration doesn't matter, controlled by rotation
        self.cross_size = self.max_cross_size
        self.cross_rotation = 0  # Start at 0 degrees
        self.has_dealt_damage = False  # Reset damage tracking
        self.can_attack = False
        self.attack_cooldown = ENEMY_ATTACK_COOLDOWN
    
    def check_circle_hit(self, player_rect):
        """Check if spinning cross has caught the player when it's small"""
        if self.attack_state != 'charging':
            return False
            
        # Check if cross is at minimum size and player is caught inside
        if self.cross_size <= self.min_cross_size and not self.has_dealt_damage:
            player_center_x = player_rect.centerx
            player_center_y = player_rect.centery
            
            distance = math.sqrt(
                (player_center_x - self.attack_center_x)**2 + 
                (player_center_y - self.attack_center_y)**2
            )
            
            # Deal damage if player is inside the small cross
            if distance <= self.cross_size:
                self.has_dealt_damage = True  # Mark that we've dealt damage
                return True
        return False
    
    def start_lightning_attack(self, player_rect):
        """Start a lightning attack at player's position"""
        # Target where player currently is
        self.lightning_target_x = player_rect.centerx
        self.lightning_target_y = player_rect.centery
        
        # Start warning phase
        self.lightning_state = 'warning'
        self.lightning_timer = 1.0  # 1 second red warning
        self.has_lightning_damaged = False
        self.can_lightning_attack = False
        self.lightning_cooldown = 3.0  # 3 second cooldown between lightning attacks
    
    def check_lightning_hit(self, player_rect):
        """Check if lightning strike hits player"""
        if self.lightning_state != 'striking' or self.has_lightning_damaged:
            return False
            
        # Check if player is inside lightning strike area (64px wide)
        strike_width = 64  # 2x player width (player is 32px)
        strike_half_width = strike_width // 2
        
        # Check if player is within the lightning pillar's horizontal range
        horizontal_distance = abs(player_rect.centerx - self.lightning_target_x)
        
        if horizontal_distance <= strike_half_width:
            self.has_lightning_damaged = True
            return True
        return False
    
    def start_evasion_dash(self, arrow):
        """Start an evasion dash to avoid incoming arrow"""
        if not self.can_dash or self.is_dashing:
            return
            
        # Determine dash direction - perpendicular to arrow trajectory
        arrow_angle = math.atan2(arrow.vel_y, arrow.vel_x)
        
        # Choose perpendicular direction (90 degrees left or right)
        if random.random() < 0.5:
            dash_angle = arrow_angle + math.pi/2  # 90 degrees left
        else:
            dash_angle = arrow_angle - math.pi/2  # 90 degrees right
            
        self.dash_direction = 1 if math.cos(dash_angle) > 0 else -1
        
        # Sometimes jump while dashing for extra evasion
        if self.on_ground and random.random() < 0.6:  # 60% chance to jump
            self.vel_y = JUMP_STRENGTH * 0.8  # Slightly lower jump
            self.on_ground = False
            self.jumps_left -= 1
        
        # Start dash
        self.is_dashing = True
        self.dash_duration = 0.3  # Dash for 0.3 seconds
        self.can_dash = False
        self.dash_cooldown = 2.0  # 2 second cooldown
    
    def start_predictive_dodge(self, player):
        """Start a predictive dodge when player is aiming"""
        # Dodge perpendicular to player's direction
        to_player_x = player.rect.centerx - self.rect.centerx
        to_player_y = player.rect.centery - self.rect.centery
        
        # Choose dodge direction (perpendicular to player direction)
        if abs(to_player_x) > abs(to_player_y):
            # Player is more horizontal, dodge vertically and horizontally
            self.dodge_direction_x = 1 if to_player_y > 0 else -1
        else:
            # Player is more vertical, dodge horizontally
            self.dodge_direction_x = 1 if to_player_x < 0 else -1
        
        # Start dodge
        self.is_dodging = True
        self.dodge_timer = 0.4  # Dodge for 0.4 seconds
        self.can_dodge = False
        self.dodge_cooldown = 1.5  # 1.5 second cooldown
        
        # Maybe jump while dodging
        if self.on_ground and random.random() < 0.6:
            self.vel_y = JUMP_STRENGTH * 0.8
            self.on_ground = False
            self.jumps_left -= 1
    
    def attack_player(self):
        """Start attack cooldown after attacking player"""
        self.can_attack = False
        self.attack_cooldown = ENEMY_ATTACK_COOLDOWN
        
    def apply_knockback(self, force_x, force_y, duration_multiplier=1.0):
        """Apply knockback to the enemy with variable force and duration"""
        # Add to existing velocity instead of replacing it (allows stacking)
        self.knockback_vel_x = force_x
        # Add upward force to current velocity instead of replacing
        self.vel_y += force_y  # Add to current velocity for natural physics
        
        # Shorter, less disruptive duration
        force_magnitude = math.sqrt(force_x*force_x + force_y*force_y)
        duration = max(0.1, (force_magnitude / 30.0))  # Shorter, simpler duration
        self.knockback_time = duration * duration_multiplier
        self.is_knocked_back = True
        
        # Trigger hit flash effect
        self.hit_flash_time = HIT_FLASH_DURATION
        self.is_flashing = True
    
    def take_damage(self, damage):
        """Take damage and update health"""
        if damage <= 0:
            return
            
        self.current_health = max(0, self.current_health - damage)
        
        # Trigger health flash effect
        self.health_flash_time = 0.2
        self.is_health_flashing = True
        
        # Check if dead
        if self.current_health <= 0:
            print("Boss defeated! Respawning...")
            self.respawn()
    
    def get_health_ratio(self):
        """Get health as a ratio (0.0 to 1.0)"""
        return self.current_health / self.max_health if self.max_health > 0 else 0.0
    
    def respawn(self):
        """Respawn the boss at spawn location with full health"""
        # Reset position
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        
        # Reset health
        self.current_health = self.max_health
        
        # Reset states
        self.vel_x = 0
        self.vel_y = 0
        self.is_knocked_back = False
        self.knockback_vel_x = 0
        self.knockback_vel_y = 0
        self.attack_state = 'idle'
        self.lightning_state = 'idle'
        self.is_dashing = False
        
        # Reset flash effects
        self.is_flashing = False
        self.is_health_flashing = False
        self.hit_flash_time = 0
        self.health_flash_time = 0
        
    def draw(self, screen, camera):
        """Draw the enemy with hit flash effect and knife"""
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        
        # Apply red flash effect when hit
        if self.is_flashing:
            # Create red-tinted version
            flash_surface = pygame.Surface(rotated_image.get_size(), pygame.SRCALPHA)
            flash_surface.fill(HIT_FLASH_COLOR + (128,))  # Semi-transparent red
            
            # Create flashed image
            flashed_image = rotated_image.copy()
            flashed_image.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_MULT)
            
            screen.blit(flashed_image, camera.apply(new_rect))
        else:
            screen.blit(rotated_image, camera.apply(new_rect))
        
        # Draw spinning cross attack
        if self.attack_state == 'charging':
            # Draw spinning red cross that shrinks
            if self.cross_size > 5:  # Only draw if size is meaningful
                cross_surface = pygame.Surface((self.cross_size * 2 + 20, self.cross_size * 2 + 20), pygame.SRCALPHA)
                
                # Make cross thickness pulse slightly
                pulse = 1.0 + 0.2 * math.sin(pygame.time.get_ticks() * 0.02)
                cross_thickness = max(3, int(6 * pulse))
                
                # Red color that gets more intense as cross gets smaller
                intensity = 1.0 - (self.cross_size / self.max_cross_size)  # 0 to 1 as it shrinks
                red_intensity = int(150 + 105 * intensity)  # 150 to 255
                red_color = (red_intensity, 0, 0, 240)
                
                # Draw spinning cross (two perpendicular lines)
                center_x = int(self.cross_size + 10)
                center_y = int(self.cross_size + 10)
                
                # Calculate rotated cross arms
                rotation_rad = math.radians(self.cross_rotation)
                cos_rot = math.cos(rotation_rad)
                sin_rot = math.sin(rotation_rad)
                
                # Horizontal arm (rotated)
                h_start_x = center_x - int(self.cross_size * cos_rot)
                h_start_y = center_y - int(self.cross_size * sin_rot)
                h_end_x = center_x + int(self.cross_size * cos_rot)
                h_end_y = center_y + int(self.cross_size * sin_rot)
                
                # Vertical arm (rotated 90 degrees from horizontal)
                v_start_x = center_x - int(self.cross_size * -sin_rot)
                v_start_y = center_y - int(self.cross_size * cos_rot)
                v_end_x = center_x + int(self.cross_size * -sin_rot)
                v_end_y = center_y + int(self.cross_size * cos_rot)
                
                # Draw the cross arms
                pygame.draw.line(cross_surface, red_color, (h_start_x, h_start_y), (h_end_x, h_end_y), cross_thickness)
                pygame.draw.line(cross_surface, red_color, (v_start_x, v_start_y), (v_end_x, v_end_y), cross_thickness)
                
                # Position cross at attack center (following player)
                cross_rect = cross_surface.get_rect(center=(self.attack_center_x, self.attack_center_y))
                screen.blit(cross_surface, camera.apply(cross_rect))
        
        # Draw lightning attack effects
        if self.lightning_state == 'warning':
            # Draw red warning pillar at target location
            warning_width = 64  # Same width as actual lightning strike
            warning_height = 600  # Full screen height pillar
            flash_intensity = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.02)  # Pulsing effect
            red_alpha = int(120 * flash_intensity)
            
            warning_surface = pygame.Surface((warning_width, warning_height), pygame.SRCALPHA)
            pygame.draw.rect(warning_surface, (255, 0, 0, red_alpha), (0, 0, warning_width, warning_height))
            
            # Add pulsing border for better visibility
            border_alpha = int(200 * flash_intensity)
            pygame.draw.rect(warning_surface, (255, 100, 100, border_alpha), (0, 0, warning_width, warning_height), 3)
            
            warning_rect = warning_surface.get_rect(centerx=self.lightning_target_x, top=0)
            screen.blit(warning_surface, camera.apply(warning_rect))
            
        elif self.lightning_state == 'striking':
            # Draw blue lightning pillar strike - 64px wide (2x player width)
            strike_width = 64
            strike_height = 600  # From top of screen down
            
            # Create lightning effect with jagged edges
            lightning_surface = pygame.Surface((strike_width + 10, strike_height), pygame.SRCALPHA)
            
            # Draw multiple lightning bolts to fill the wider area
            for bolt in range(3):  # 3 lightning bolts across the width
                points = []
                bolt_x_center = (strike_width // 4) + bolt * (strike_width // 3)
                
                for i in range(0, strike_height, 15):
                    x_offset = random.randint(-8, 8)  # More jagged effect
                    points.append((bolt_x_center + x_offset, i))
                
                if len(points) >= 2:
                    # Main bolt
                    pygame.draw.lines(lightning_surface, (80, 120, 255, 200), False, points, 12)
                    pygame.draw.lines(lightning_surface, (150, 180, 255, 180), False, points, 8)
                    pygame.draw.lines(lightning_surface, (220, 240, 255, 160), False, points, 4)
                    pygame.draw.lines(lightning_surface, (255, 255, 255, 100), False, points, 2)
            
            # Add overall glow effect for the pillar
            glow_rect = pygame.Rect(5, 0, strike_width, strike_height)
            pygame.draw.rect(lightning_surface, (50, 100, 255, 30), glow_rect)
            
            # Position lightning at target
            lightning_rect = lightning_surface.get_rect(centerx=self.lightning_target_x, top=0)
            screen.blit(lightning_surface, camera.apply(lightning_rect))
    
    def draw_boss_health_bar(self, screen, screen_width, screen_height):
        """Draw boss health bar in top right corner"""
        # Boss bar dimensions - 1/3 of screen width
        bar_width = screen_width // 3
        bar_height = 30
        bar_x = screen_width - bar_width - 20  # 20px margin from right edge
        bar_y = 20  # 20px from top
        
        # Background bar
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (50, 50, 50), bg_rect)  # Dark gray background
        pygame.draw.rect(screen, (200, 200, 200), bg_rect, 2)  # Light gray border
        
        # Health bar fill
        if self.current_health > 0:
            health_ratio = self.get_health_ratio()
            fill_width = int(bar_width * health_ratio)
            
            # Color based on health percentage
            if health_ratio > 0.6:
                health_color = (255, 100, 100)  # Red
            elif health_ratio > 0.3:
                health_color = (255, 150, 0)    # Orange  
            else:
                health_color = (255, 50, 50)    # Dark red
            
            # Apply flash effect if taking damage
            if self.is_health_flashing:
                flash_intensity = (self.health_flash_time / 0.2)
                flash_color = (255, 255, 255)
                # Interpolate between health color and white
                health_color = (
                    int(health_color[0] + (flash_color[0] - health_color[0]) * flash_intensity),
                    int(health_color[1] + (flash_color[1] - health_color[1]) * flash_intensity),
                    int(health_color[2] + (flash_color[2] - health_color[2]) * flash_intensity)
                )
            
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(screen, health_color, fill_rect)
        
        # Boss name and health text INSIDE the bar
        font = pygame.font.Font(None, 20)  # Slightly smaller to fit inside
        boss_text = f"BOSS PIG: {int(self.current_health)}/{self.max_health}"
        text_surface = font.render(boss_text, True, (255, 255, 255))
        
        # Add text shadow for better readability
        shadow_surface = font.render(boss_text, True, (0, 0, 0))
        shadow_x = bar_x + (bar_width - shadow_surface.get_width()) // 2 + 1
        shadow_y = bar_y + (bar_height - shadow_surface.get_height()) // 2 + 1
        screen.blit(shadow_surface, (shadow_x, shadow_y))
        
        # Main text
        text_x = bar_x + (bar_width - text_surface.get_width()) // 2
        text_y = bar_y + (bar_height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))