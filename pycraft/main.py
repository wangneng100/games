import pygame
from pygame.locals import *
import sys
import os

from settings import *
from player import Player
from bow import Bow
from camera import Camera
from item import BowItem, KnifeItem
from enemy import Enemy
from melee import Knife

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
        
        # Load knife image (uses sword.png)
        knife_img_path = os.path.join(assets_dir, 'texture', 'sword.png')
        knife_img = pygame.image.load(knife_img_path).convert_alpha()
        knife_avg_color = pygame.transform.average_color(knife_img)
        
        # Load arrow image
        arrow_img_path = os.path.join(assets_dir, 'texture', 'arrow.png')
        arrow_img = pygame.image.load(arrow_img_path).convert_alpha()
        arrow_h = PLAYER_HEIGHT * ARROW_SIZE
        arrow_w = int(arrow_img.get_width() * (arrow_h / arrow_img.get_height()))
        arrow_img = pygame.transform.scale(arrow_img, (arrow_w, arrow_h))
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
    # X = Ground Block
    level_map = [
        "                                                                                ",
        "                                                                                ",
        "                                                                                ",
        "       XXXXX                                       XXXXX                        ",
        "                                                                                ",
        "   XX               XX                          XXXXXX                          ",
        "                                                                                ",
        "               XXXX                       XXXXX                                 ",
        "      XXXX            XXXXXX                                                          ",
        "                            XXXXX                                 XXXXXXXXXXXXX ",
        "  XXXXXX         XXXX                           XXXXX                           ",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX        XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX        XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
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
    knife = Knife(knife_img, knife_avg_color)
    player = Player(100, 10 * TILE_SIZE - PLAYER_HEIGHT, player_img, bow, knife)
    
    # Create items and add to hotbar
    bow_item = BowItem(bow, bow_img)
    knife_item = KnifeItem(knife, knife_img)
    player.hotbar.add_item(bow_item, 0)    # Add bow to slot 1
    player.hotbar.add_item(knife_item, 1)  # Add knife to slot 2
    player.hotbar.select_slot(0)  # Start with bow selected
    
    # Create test enemy
    enemy = Enemy(400, 8 * TILE_SIZE - PLAYER_HEIGHT, player_img)  # Use same image as player
    
    print("Bow, Player, Hotbar, and Enemy created.")
    
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
        enemy.update(platforms, player.rect)  # Update enemy AI
        
        # Check collisions
        player.check_enemy_collision(enemy)
        player.check_arrow_hits(enemy)
        
        # Only check knife hits when knife is equipped
        if player.current_weapon == player.knife:
            player.check_knife_hit(enemy)

        
        camera.update(player.rect, mouse_pos)

        screen.fill(SKY_BLUE)
        for platform in platforms:
            screen.blit(dirt_img, camera.apply(platform))
        
        player.draw(screen, camera)

        enemy.draw(screen, camera)  # Draw enemy
        player.draw_hotbar(screen)  # Draw hotbar UI
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()