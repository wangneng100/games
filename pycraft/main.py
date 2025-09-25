import pygame
from pygame.locals import *
import sys
import os

from settings import *
from player import Player
from staff import Staff
from camera import Camera

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
        staff_img_path = os.path.join(assets_dir, 'texture', 'staff.png')
        staff_img = pygame.image.load(staff_img_path).convert_alpha()
        staff_h = PLAYER_HEIGHT * 3.5
        staff_w = int(staff_img.get_width() * (staff_h / staff_img.get_height()))
        staff_img = pygame.transform.scale(staff_img, (staff_w, staff_h))
        avg_color = pygame.transform.average_color(staff_img)
        gray = (128, 128, 128)
        avg_color = (
            (avg_color[0] + gray[0]) // 2,
            (avg_color[1] + gray[1]) // 2,
            (avg_color[2] + gray[2]) // 2,
        )
        print("Images loaded successfully.")
    except pygame.error as e:
        print(f"Unable to load image: {e}")
        print("\nMake sure you have an 'assets/texture' folder with 'player.png' and 'dirt.png' inside.")
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
    player = Player(100, 10 * TILE_SIZE - PLAYER_HEIGHT, player_img, staff)
    print("Staff and Player created.")
    
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

        left_click, _, _ = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        player.update(platforms, jump_pressed, left_click, camera, jump_key_released)
        camera.update(player.rect, mouse_pos)

        screen.fill(SKY_BLUE)
        for platform in platforms:
            screen.blit(dirt_img, camera.apply(platform))
        
        player.draw(screen, camera)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()