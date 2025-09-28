import pygame
from pygame.locals import *
import sys
import os
import math
import random

from settings import *
from player import Player
from bow import Bow
from camera import Camera
from item import BowItem
from dummy_enemy import Enemy
from particle import ParticleSystem

def main():
    """Main game function."""
    print("Starting main function...")
    pygame.init()
    print("Pygame initialized.")

    info = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
    print("Attempting to create screen...")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    print(f"Screen created: {SCREEN_WIDTH}x{SCREEN_HEIGHT} fullscreen.")
    
    pygame.display.set_caption("Python Platformer")
    clock = pygame.time.Clock()

    # --- Load Images ---
    # Build absolute paths to assets to make the game runnable from anywhere
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, 'assets')
    try:
        player_img_path = os.path.join(assets_dir, 'texture', 'player.png')
        player_img = pygame.image.load(player_img_path).convert_alpha()
        player_img = pygame.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
        dirt_img_path = os.path.join(assets_dir, 'texture', 'dirt.png')
        dirt_img = pygame.image.load(dirt_img_path).convert()
        dirt_img = pygame.transform.scale(dirt_img, (TILE_SIZE, TILE_SIZE))
        
        # Load bow image
        bow_img_path = os.path.join(assets_dir, 'texture', 'bow.png')
        bow_img = pygame.image.load(bow_img_path).convert_alpha()
        bow_h = PLAYER_HEIGHT * BOW_SIZE
        bow_w = int(bow_img.get_width() * (bow_h / bow_img.get_height()))
        bow_img = pygame.transform.scale(bow_img, (bow_w, bow_h))
        

        
        # Load arrow image
        arrow_img_path = os.path.join(assets_dir, 'texture', 'arrow.png')
        arrow_img = pygame.image.load(arrow_img_path).convert_alpha()
        arrow_h = PLAYER_HEIGHT * ARROW_SIZE
        arrow_w = int(arrow_img.get_width() * (arrow_h / arrow_img.get_height()))
        arrow_img = pygame.transform.scale(arrow_img, (arrow_w, arrow_h))
        
        # Load staff image for enemy
        staff_img_path = os.path.join(assets_dir, 'texture', 'staff.png')
        staff_img = pygame.image.load(staff_img_path).convert_alpha()
        staff_h = PLAYER_HEIGHT * 2  # Make staff bigger than player
        staff_w = int(staff_img.get_width() * (staff_h / staff_img.get_height()))
        staff_img = pygame.transform.scale(staff_img, (staff_w, staff_h))
        
        # Create lighter blue gradient background for better motion blur visibility
        bg_img = pygame.Surface((SCREEN_WIDTH + 200, SCREEN_HEIGHT + 200))
        # Create vertical gradient from light blue to lighter blue
        for y in range(SCREEN_HEIGHT + 200):
            # Interpolate between light blue and lighter blue
            progress = y / (SCREEN_HEIGHT + 200)
            light_blue = (120, 160, 200)  # Light blue at top
            lighter_blue = (180, 220, 255)  # Lighter blue at bottom
            
            # Blend colors
            r = int(light_blue[0] * (1 - progress) + lighter_blue[0] * progress)
            g = int(light_blue[1] * (1 - progress) + lighter_blue[1] * progress)
            b = int(light_blue[2] * (1 - progress) + lighter_blue[2] * progress)
            
            pygame.draw.line(bg_img, (r, g, b), (0, y), (SCREEN_WIDTH + 200, y))
        print("Images loaded successfully.")
    except pygame.error as e:
        print(f"Unable to load image: {e}")
        print("\nMake sure you have an 'assets/texture' folder with required images inside.")
        pygame.quit()
        sys.exit()

    # --- Load Cursor ---
    try:
        cursor_img_path = os.path.join(assets_dir, 'texture', 'cursor.png')
        cursor_img = pygame.image.load(cursor_img_path).convert_alpha()
        cursor_size = (PLAYER_WIDTH // 2, PLAYER_HEIGHT // 2)
        cursor_img = pygame.transform.scale(cursor_img, cursor_size)
        hotspot = (cursor_img.get_width() // 2, cursor_img.get_height() // 2)
        cursor = pygame.cursors.Cursor(hotspot, cursor_img)
        pygame.mouse.set_cursor(cursor)
        print("Cursor loaded and set.")
    except pygame.error as e:
        print(f"Unable to load cursor image: {e}")

    # --- Load Sound ---
    try:
        bgm_path = os.path.join(assets_dir, 'sound', 'bgm.mp3')
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.play(-1)  # Play on loop
        print("BGM loaded and playing.")
    except pygame.error as e:
        print(f"Unable to load or play BGM: {e}")

    # --- Level Data ---
    # X = Ground Block - Flat map for easier combat
    level_map = [
        "                                                                                ",
        "                                                                                ",
        "                                                                                ",
        "                                                                                ",
        "                                                                                ",
        "                                                                                ",
        "                                                                                ",
        "                                                                                ",
        "                                                                                ",
        "                                                                                ",
        "                                                                                ",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    ]

    platforms = []
    for row_index, row in enumerate(level_map):
        for col_index, tile in enumerate(row):
            if tile == 'X':
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                platforms.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
    print("Level data and platforms created.")

    bow = Bow(bow_img, arrow_img)
    player = Player(100, 10 * TILE_SIZE - PLAYER_HEIGHT, player_img, bow)
    
    # Create items and add to hotbar
    bow_item = BowItem(bow, bow_img)
    player.hotbar.add_item(bow_item, 0)    # Add bow to slot 1
    player.hotbar.select_slot(0)  # Start with bow selected
    
    # Create particle system
    particle_system = ParticleSystem()
    
    # Create 10 DEADLY ARCHER ENEMIES spawned ON PLATFORMS!
    enemies = []
    # Find platform positions and spawn enemies on them
    platform_positions = []
    for row_index, row in enumerate(level_map):
        for col_index, tile in enumerate(row):
            if tile == 'X':  # Platform tile
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE - PLAYER_HEIGHT  # Spawn on top of platform
                platform_positions.append((x, y))
    
    # Select 1 random platform position for enemy
    selected_positions = random.sample(platform_positions, min(1, len(platform_positions)))
    
    for i, (x, y) in enumerate(selected_positions):
        enemy = Enemy(x, y, player_img, bow_img)
        enemy.particle_system = particle_system  # Connect particle system to enemy
        # Make enemy bow point at player initially
        dx = player.rect.centerx - enemy.rect.centerx
        dy = player.rect.centery - enemy.rect.centery
        enemy.angle = math.atan2(dy, dx)
        enemies.append(enemy)
        print(f"Spawned enemy #{i+1} on platform at ({x}, {y})")
    
    # Give player reference to first enemy for aimbot assist
    player.enemy_target = enemies[0] if enemies else None
    
    print("Bow, Player, Hotbar, Enemy, and ParticleSystem created.")
    
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    print("Camera created.")

    # --- Game Loop ---
    print("Entering game loop.")
    running = True
    while running:
        jump_pressed = False
        jump_key_released = False
        dash_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_UP or event.key == K_w:
                    jump_pressed = True
                if event.key == K_SPACE:
                    dash_pressed = True
                # Health testing keys
                if event.key == K_h:  # H key to take normal damage
                    player.take_damage(10)
                if event.key == K_v:  # V key for void damage
                    player.take_damage(100, is_void=True)
                if event.key == K_g:  # G key to heal
                    player.heal(20)
            if event.type == KEYUP:
                if event.key == K_UP or event.key == K_w:
                    jump_key_released = True
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if clicking on hotbar
                    player.handle_hotbar_click(event.pos)
                elif event.button == 4:  # Mouse wheel up
                    player.handle_hotbar_scroll(1)
                elif event.button == 5:  # Mouse wheel down
                    player.handle_hotbar_scroll(-1)

        left_click, _, right_click = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()
        player.update(platforms, jump_pressed, left_click, camera, jump_key_released, right_click, keys_pressed, mouse_pos, dash_pressed)
        # Update all 10 enemies - THEY'RE ALL HUNTING YOU!
        for enemy in enemies:
            enemy.update(platforms, player, particle_system)  # Update enemy AI with particle system
            
            # Check collision between player and enemy
            player.check_enemy_collision(enemy)
            player.check_arrow_hits(enemy)
            
            # Check if enemy arrows hit player!
            for arrow in enemy.arrows[:]:
                if arrow.alive and arrow.rect.colliderect(player.rect):
                    if hasattr(arrow, 'is_enemy_arrow') and arrow.is_enemy_arrow:
                        player.take_damage(arrow.damage)
                        print(f"Player hit by enemy arrow! Damage: {arrow.damage}")
                        arrow.alive = False
                        enemy.arrows.remove(arrow)
        
        particle_system.update()  # Update particles
        
        # Staff attacks now create particle explosions instead of direct damage
        
        # Check if particles hit player
        particle_damage = particle_system.check_player_collisions(player.rect)
        if particle_damage > 0:
            player.take_damage(particle_damage)
            print(f"Particle hit! Damage: {particle_damage}, Player health: {player.health_bar.current_health}")
        
        # No more lightning system - removed for cleaner gameplay
        


        
        camera.update(player.rect, mouse_pos)
        
        # Draw static background (no parallax to avoid screen edge issues)
        screen.blit(bg_img, (0, 0))
        # Draw darker platforms for contrast
        for platform in platforms:
            # Create darkened dirt image
            dark_dirt = dirt_img.copy()
            dark_overlay = pygame.Surface(dirt_img.get_size())
            dark_overlay.fill((0, 0, 0))
            dark_overlay.set_alpha(120)  # 50% darker
            dark_dirt.blit(dark_overlay, (0, 0))
            screen.blit(dark_dirt, camera.apply(platform))
        
        player.draw(screen, camera)

        # Draw all 10 enemies - AN ARMY OF ARCHERS!
        for enemy in enemies:
            enemy.draw(screen, camera, player)  # Draw enemy with player reference for bow aiming
        
        particle_system.draw(screen, camera)  # Draw particles
        
        # Draw health bars for first few enemies (not all 10 to avoid clutter)
        for i, enemy in enumerate(enemies[:3]):  # Show health for first 3 enemies
            enemy.draw_boss_health_bar(screen, SCREEN_WIDTH, SCREEN_HEIGHT + i * 30)
        
        player.draw_hotbar(screen)  # Draw hotbar UI
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()