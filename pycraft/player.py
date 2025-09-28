import pygame
import math
import time
from settings import *
from hotbar import Hotbar
from trail import Trail

class Player:
    """Represents the player character."""
    def __init__(self, x, y, image, bow):
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
        # Initialize arrow list for tracking
        self.arrows = []
        
        # ENHANCED MOTION BLUR SYSTEM for player (walking + dashing)
        self.motion_blur_copies = []  # List to store multiple player positions
        self.max_blur_copies = 120  # Optimized for walking + dashing blur
        self.blur_alpha_decay = 0.88  # Faster fade for cleaner trails
        
        # Initialize health bar
        from health_bar import HealthBar
        self.health_bar = HealthBar(max_health=1000)  # 10x more HP
        self.spawn_x = x
        self.spawn_y = y
        
        # Natural regeneration system
        self.regen_timer = 0  # Timer for natural healing
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
        
        # Knockback system with variable speed
        self.knockback_vel_x = 0
        self.knockback_vel_y = 0
        self.knockback_time = 0
        self.is_knocked_back = False
        self.initial_knockback_x = 0
        self.initial_knockback_y = 0
        
        # Mana system for special abilities
        self.mana = 0  # Current mana (0-20)
        self.max_mana = 20  # Maximum mana
        self.mana_bar_alpha = 255  # For golden glow effect
        
        # Special ability system
        self.is_special_ability_active = False
        self.special_ability_timer = 0
        self.special_arrow_cooldown = 0

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
        
        # Reset health tank
        self.health_bar.reset()

    def update(self, platforms, jump_pressed, left_click, camera, jump_key_released, right_click, keys_pressed=None, mouse_pos=None, dash_pressed=False):
        """Handles player movement, gravity, and collision."""
        # Natural regeneration - 1 HP per second
        self.regen_timer += 1/60  # Assuming 60 FPS
        if self.regen_timer >= 1.0:  # Every 1 second
            self.heal(1)  # Heal 1 HP
            self.regen_timer = 0

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
            
        # --- Handle special ability activation ---
        if keys_pressed and keys_pressed[pygame.K_s] and self.mana >= 20 and not self.is_special_ability_active:
            self.activate_special_ability()
        
        # --- Handle dash input ---
        if dash_pressed and not self.is_dashing:
            # Check if dash is off cooldown
            if current_time - self.dash_cooldown_start >= DASH_COOLDOWN:
                self.start_dash(keys_pressed)
                
        # Update dash state
        if self.is_dashing:
            if current_time - self.dash_start_time >= DASH_DURATION:
                self.is_dashing = False
            else:
                # Add position to dash trail
                self.dash_trail.add_position(self.rect.centerx, self.rect.centery)
                
        # --- Handle weapon attacks based on current weapon ---
        
        # Only handle bow mechanics when bow is equipped
        if self.current_weapon == self.bow:
            # Special ability rapid fire
            if self.is_special_ability_active:
                self.special_arrow_cooldown -= 1/60  # Assuming 60 FPS
                if self.special_arrow_cooldown <= 0:
                    arrow = self.bow.shoot_arrow(self.enemy_target)  # Pass enemy for aimbot assist
                    if arrow:
                        arrow.particle_system = self.particle_system
                        self.arrows.append(arrow)
                    self.special_arrow_cooldown = 0.1  # Shoot every 0.1 seconds (10 arrows/sec)
            
            # Normal bow mechanics
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
        

        
        # Update arrows
        self.arrows = [arrow for arrow in self.arrows if arrow.alive]
        for arrow in self.arrows:
            arrow.update(platforms)
            
        # Update particle system
        self.particle_system.update()
        
        # Update health tank
        self.health_bar.update()
        
        # SUPER MOTION BLUR UPDATE - Add current position to blur trail
        total_velocity = abs(self.vel_x) + abs(self.vel_y)
        if total_velocity > 0.5:  # Only add blur when moving
            # Dynamic blur count based on speed (faster = MORE BLUR)
            speed_multiplier = min(total_velocity / 5.0, 3.0)  # Cap at 3x multiplier
            dynamic_max_copies = int(self.max_blur_copies * speed_multiplier)
            dynamic_max_copies = max(20, dynamic_max_copies)  # Minimum 20 copies
            
            # Add current position to blur trail
            if len(self.motion_blur_copies) >= dynamic_max_copies:
                self.motion_blur_copies.pop(0)  # Remove oldest copy
            
            # CREATE MOTION BLUR - strong for dashing, weak for walking
            player_speed = math.sqrt(self.vel_x**2 + self.vel_y**2)
            if self.is_dashing:
                # Strong blur when dashing
                alpha = 70  # Strong dash blur
                self.motion_blur_copies.append({
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'angle': self.angle,
                    'alpha': alpha,
                    'image': self.image.copy()
                })
            elif player_speed > 1.0:  # Walking/moving blur
                # Weak blur for normal movement
                alpha = 25  # Much weaker walking blur
                self.motion_blur_copies.append({
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'angle': self.angle,
                    'alpha': alpha,
                    'image': self.image.copy()
                })
        
        # Fade existing blur copies (adjusted for lighter background)
        for i in range(len(self.motion_blur_copies) - 1, -1, -1):
            self.motion_blur_copies[i]['alpha'] *= self.blur_alpha_decay
            if self.motion_blur_copies[i]['alpha'] < 8:  # Remove very faded copies
                self.motion_blur_copies.pop(i)
        
        # Update special ability
        if self.is_special_ability_active:
            self.special_ability_timer -= 1/60  # Assuming 60 FPS
            if self.special_ability_timer <= 0:
                self.is_special_ability_active = False
        
        # Continuous death check
        if self.health_bar.current_health <= 0:
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
    
    def activate_special_ability(self):
        """Activate special ability: launch into air and rapid fire for 5 seconds"""
        # Use all mana
        self.mana = 0
        self.mana_bar_alpha = 255  # Reset glow
        
        # Launch player into the air
        self.vel_y = -25  # Strong upward velocity
        self.on_ground = False
        
        # Activate rapid fire mode
        self.is_special_ability_active = True
        self.special_ability_timer = 5.0  # 5 seconds
        self.special_arrow_cooldown = 0  # Reset arrow cooldown

    def draw(self, screen, camera):
        """Draws the player on the screen with SUPER MOTION BLUR."""
        
        # DRAW MOTION BLUR COPIES FIRST (behind main player)
        for copy in self.motion_blur_copies:
            if copy['alpha'] > 10:  # Only draw visible copies
                # Rotate the blur copy
                blur_rotated = pygame.transform.rotate(copy['image'], copy['angle'])
                blur_rect = blur_rotated.get_rect(center=(copy['x'], copy['y']))
                
                # Apply alpha transparency for blur effect
                blur_surface = blur_rotated.copy()
                blur_surface.set_alpha(int(copy['alpha']))
                
                # Draw the blur copy
                screen.blit(blur_surface, camera.apply(blur_rect))

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
            # Draw player normally without any brightness overlay
            screen.blit(rotated_image, camera.apply(new_rect))
        
        # Draw current equipped weapon
        if self.current_weapon == self.bow:
            self.bow.draw(screen, camera)

        
        # Draw arrows
        for arrow in self.arrows:
            arrow.draw(screen, camera)
            
        # Draw dash trail
        if self.is_dashing:
            self.dash_trail.draw(screen, camera)
            
        # Draw particles
        self.particle_system.draw(screen, camera)
        
        # Draw health tank (UI element - not affected by camera)
        self.health_bar.draw(screen)
            
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
        """INSANE MODE: Boss damages player on contact!"""
        if self.rect.colliderect(enemy.rect):
            # INSANE MODE: Boss deals contact damage to player!
            if not hasattr(self, 'last_contact_damage_time'):
                self.last_contact_damage_time = 0
            
            current_time = time.time()
            if current_time - self.last_contact_damage_time > 0.5:  # Contact damage every 0.5 seconds
                contact_damage = 15  # Boss deals damage on touch
                self.take_damage(contact_damage)
                self.last_contact_damage_time = current_time
                print(f"Boss contact damage! Player took {contact_damage} damage!")
                
                # Push player away from boss
                dx = self.rect.centerx - enemy.rect.centerx
                dy = self.rect.centery - enemy.rect.centery
                if dx != 0 and dy != 0:
                    self.vel_x += dx * 0.3
                    self.vel_y += dy * 0.2

                
    def check_arrow_hits(self, enemy):
        """Check if arrows hit the enemy with smaller hitbox"""
        for arrow in self.arrows[:]:
            if arrow.alive:
                # Create center-based hitbox for arrow
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
                    
                    # INSANE MODE: No stuns, boss is relentless!
                    # Boss takes damage but never stops attacking
                    if hasattr(enemy, 'is_jumping') and enemy.is_jumping:
                        # Boss takes extra damage during spin but doesn't stop!
                        print("Hit boss during death spin - extra damage but boss continues!")
                        # Apply stronger knockback but boss keeps attacking
                        enemy.apply_knockback(dx * 1.5, dy * 1.5, 0.3)  # Stronger but shorter knockback
                    else:
                        # Apply normal knockback to enemy
                        enemy.apply_knockback(dx, dy, 0.5)  # Shorter knockback
                    
                    # Damage enemy based on arrow charge power (100x weaker than original)
                    base_damage = 0.15  # Base damage (was 1.5, originally 15)
                    charge_bonus = 0.35 * arrow.charge_power  # 0-0.35 bonus damage based on charge (was 0-3.5, originally 0-35)
                    total_damage = base_damage + charge_bonus  # 0.15-0.5 total damage (was 1.5-5, originally 15-50)
                    enemy.take_damage(total_damage)
                    
                    # GAIN MANA on hit!
                    if self.mana < self.max_mana:
                        self.mana += 1
                        print(f"Arrow hit! Enemy damaged. Mana: {self.mana}/{self.max_mana}")
                    
                    # Remove arrow
                    arrow.alive = False
        
        # Clean up dead arrows
        self.arrows = [arrow for arrow in self.arrows if arrow.alive]
    

    
    def take_damage(self, damage, is_void=False):
        """Take damage and update health tank"""
        self.health_bar.take_damage(damage, is_void)
        
        # Trigger damage flash effect
        self.damage_flash_time = 0.3  # Flash for 0.3 seconds
        self.is_damage_flashing = True
        
        # Always check if dead after taking damage
        if self.health_bar.current_health <= 0:
            self.reset()  # Reset player when dead
    
    def heal(self, amount):
        """Heal player"""
        self.health_bar.heal(amount)
    
    def draw_hotbar(self, screen):
        """Draw the hotbar and mana bar UI"""
        self.hotbar.draw(screen)
        
        # Draw mana bar
        mana_bar_x = 20
        mana_bar_y = 120  # Below health bar
        mana_bar_width = 160
        mana_bar_height = 15
        
        # Background
        pygame.draw.rect(screen, (40, 40, 40), (mana_bar_x - 2, mana_bar_y - 2, mana_bar_width + 4, mana_bar_height + 4))
        pygame.draw.rect(screen, (60, 60, 60), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height))
        
        # Mana fill
        mana_ratio = self.mana / self.max_mana
        mana_fill_width = int(mana_bar_width * mana_ratio)
        if self.mana >= self.max_mana:
            # Full mana - golden glow
            pygame.draw.rect(screen, (255, 215, 0), (mana_bar_x, mana_bar_y, mana_fill_width, mana_bar_height))
        else:
            # Building mana - blue
            pygame.draw.rect(screen, (100, 150, 255), (mana_bar_x, mana_bar_y, mana_fill_width, mana_bar_height))
        
        # Mana text
        font = pygame.font.Font(None, 24)
        mana_text = f"MANA: {self.mana}/{self.max_mana}"
        if self.mana >= self.max_mana:
            mana_text += " - PRESS S FOR SPECIAL!"
        text_surface = font.render(mana_text, True, (255, 255, 255))
        screen.blit(text_surface, (mana_bar_x, mana_bar_y + mana_bar_height + 5))
