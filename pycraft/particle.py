import pygame
import math
import random
from settings import *

class Particle:
    """Individual particle for explosion effects"""
    def __init__(self, x, y, vel_x, vel_y, color, lifetime, can_damage=False, damage=5):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alive = True
        self.size = PARTICLE_SIZE
        self.can_damage = can_damage  # Whether this particle can damage the player
        self.damage = damage  # How much damage it deals
        self.has_hit_player = False  # Track if this particle already hit the player
        
    def update(self):
        """Update particle physics"""
        if not self.alive:
            return
            
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Apply gravity and air resistance
        self.vel_y += 0.2  # Gravity
        self.vel_x *= 0.98  # Air resistance
        self.vel_y *= 0.98
        
        # Update lifetime
        self.lifetime -= 1/60  # Assuming 60 FPS
        if self.lifetime <= 0:
            self.alive = False
    
    def check_collision(self, player_rect):
        """Check if particle collides with player"""
        if not self.alive or not self.can_damage or self.has_hit_player:
            return False
            
        # Create particle hitbox
        particle_rect = pygame.Rect(
            self.x - self.size, self.y - self.size, 
            self.size * 2, self.size * 2
        )
        
        # Check collision with player
        if particle_rect.colliderect(player_rect):
            self.has_hit_player = True  # Mark as hit so it doesn't hit again
            return True
        return False
            
    def draw(self, screen, camera):
        """Draw the particle"""
        if not self.alive:
            return
            
        # Calculate alpha based on remaining lifetime
        alpha_factor = self.lifetime / self.max_lifetime
        alpha = int(255 * alpha_factor)
        
        # Calculate size based on lifetime (shrinks over time)
        current_size = int(self.size * alpha_factor)
        if current_size < 1:
            current_size = 1
            
        # Apply camera transform
        screen_pos = camera.apply_point((self.x, self.y))
        
        # Draw particle as a small circle
        if alpha > 0:
            color_with_alpha = (*self.color, alpha)
            # Create a small surface for the particle
            particle_surface = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color_with_alpha, (current_size, current_size), current_size)
            screen.blit(particle_surface, (screen_pos[0] - current_size, screen_pos[1] - current_size))

class ParticleSystem:
    """Manages multiple particles"""
    def __init__(self):
        self.particles = []
        
    def create_explosion(self, x, y, color, count=PARTICLE_COUNT, can_damage=False, damage=5):
        """Create an explosion of particles at the given position"""
        for _ in range(count):
            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX)
            
            # Calculate velocity
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # Add some randomness to lifetime
            lifetime = PARTICLE_LIFETIME + random.uniform(-0.2, 0.2)
            
            # Create particle (with damage capability if specified)
            particle = Particle(x, y, vel_x, vel_y, color, lifetime, can_damage, damage)
            self.particles.append(particle)
            
    def update(self):
        """Update all particles"""
        # Update particles
        for particle in self.particles:
            particle.update()
            
        # Remove dead particles
        self.particles = [p for p in self.particles if p.alive]
        
    def check_player_collisions(self, player_rect):
        """Check if any particles hit the player and return damage dealt"""
        total_damage = 0
        for particle in self.particles:
            if particle.check_collision(player_rect):
                total_damage += particle.damage
        return total_damage
    
    def draw(self, screen, camera):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen, camera)