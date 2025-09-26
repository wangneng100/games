import pygame
from pygame.locals import *
import sys
import os

from settings import *
from player import Player
from bow import Bow
from staff import Staff
from camera import Camera
from item import SwordItem, BowItem

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
        # Load staff image
        staff_img_path = os.path.join(assets_dir, 'texture', 'sword.png')
        staff_img = pygame.image.load(staff_img_path).convert_alpha()
        staff_h = PLAYER_HEIGHT * STAFF_SIZE
        staff_w = int(staff_img.get_width() * (staff_h / staff_img.get_height()))
        staff_img = pygame.transform.scale(staff_img, (staff_w, staff_h))
        avg_color = pygame.transform.average_color(staff_img)
        gray = (128, 128, 128)
        avg_color = (
            (avg_color[0] + gray[0]) // 2,
            (avg_color[1] + gray[1]) // 2,
            (avg_color[2] + gray[2]) // 2,
        )
        
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

    staff = Staff(staff_img, avg_color)
    bow = Bow(bow_img, arrow_img)
    player = Player(100, 10 * TILE_SIZE - PLAYER_HEIGHT, player_img, staff, bow)
    
    # Create items and add to hotbar
    sword_item = SwordItem(staff, staff_img)
    bow_item = BowItem(bow, bow_img)
    player.hotbar.add_item(sword_item, 0)  # Add sword to slot 1
    player.hotbar.add_item(bow_item, 1)    # Add bow to slot 2
    player.hotbar.select_slot(0)  # Start with sword selected
    
    print("Staff, Bow, Player, and Hotbar created.")
    
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    print("Camera created.")

    # --- Game Loop ---
    print("Entering game loop.")
    running = True
    while running:
        jump_pressed = False
        jump_key_released = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_SPACE or event.key == K_UP or event.key == K_w:
                    jump_pressed = True
            if event.type == KEYUP:
                if event.key == K_SPACE or event.key == K_UP or event.key == K_w:
                    jump_key_released = True
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if clicking on hotbar
                    player.handle_hotbar_click(event.pos)

        left_click, _, right_click = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()
        player.update(platforms, jump_pressed, left_click, camera, jump_key_released, right_click, keys_pressed, mouse_pos)
        camera.update(player.rect, mouse_pos)

        screen.fill(SKY_BLUE)
        for platform in platforms:
            screen.blit(dirt_img, camera.apply(platform))
        
        player.draw(screen, camera)
        player.draw_hotbar(screen)  # Draw hotbar UI
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()