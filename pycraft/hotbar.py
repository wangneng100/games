import pygame
from settings import *

class Hotbar:
    """Hotbar UI system for item management"""
    def __init__(self):
        self.slots = [None] * HOTBAR_SLOTS  # 12 slots for items
        self.selected_slot = 0  # Currently selected slot
        self.slot_rects = []  # For mouse click detection
        
        # Calculate slot positions (horizontal layout)
        for i in range(HOTBAR_SLOTS):
            slot_x = HOTBAR_X + i * (HOTBAR_SLOT_SIZE + HOTBAR_PADDING)
            rect = pygame.Rect(slot_x, HOTBAR_Y, HOTBAR_SLOT_SIZE, HOTBAR_SLOT_SIZE)
            self.slot_rects.append(rect)
    
    def add_item(self, item, slot=None):
        """Add an item to a specific slot or first empty slot"""
        if slot is not None and 0 <= slot < HOTBAR_SLOTS:
            self.slots[slot] = item
            return True
        else:
            # Find first empty slot
            for i in range(HOTBAR_SLOTS):
                if self.slots[i] is None:
                    self.slots[i] = item
                    return True
            return False  # No empty slots
    
    def get_selected_item(self):
        """Get the currently selected item"""
        return self.slots[self.selected_slot]
    
    def select_slot(self, slot_index):
        """Select a specific slot"""
        if 0 <= slot_index < HOTBAR_SLOTS:
            self.selected_slot = slot_index
    
    def handle_key_input(self, keys_pressed):
        """Handle keyboard input for slot selection"""
        for i, key in enumerate(HOTBAR_KEYS):
            if keys_pressed[key]:
                self.select_slot(i)
                return True
        return False
    
    def handle_mouse_click(self, mouse_pos):
        """Handle mouse clicks on hotbar slots"""
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                self.select_slot(i)
                return True
        return False
    
    def handle_scroll(self, scroll_direction):
        """Handle mouse wheel scrolling for hotbar"""
        if scroll_direction > 0:  # Scroll up
            new_slot = (self.selected_slot - 1) % HOTBAR_SLOTS
        else:  # Scroll down
            new_slot = (self.selected_slot + 1) % HOTBAR_SLOTS
        self.select_slot(new_slot)
        return True
    
    def draw(self, screen):
        """Draw the hotbar on screen"""
        # Create surface with alpha for transparency (horizontal layout)
        hotbar_surface = pygame.Surface((HOTBAR_SLOTS * (HOTBAR_SLOT_SIZE + HOTBAR_PADDING) + HOTBAR_PADDING, 
                                        HOTBAR_SLOT_SIZE + HOTBAR_PADDING * 2), 
                                       pygame.SRCALPHA)
        hotbar_surface.fill(HOTBAR_BACKGROUND_COLOR)
        
        # Draw background
        screen.blit(hotbar_surface, (HOTBAR_X - HOTBAR_PADDING, HOTBAR_Y - HOTBAR_PADDING))
        
        # Draw slots
        for i, rect in enumerate(self.slot_rects):
            # Determine border color
            if i == self.selected_slot:
                border_color = HOTBAR_SELECTED_COLOR
                border_width = 3
            else:
                border_color = HOTBAR_BORDER_COLOR
                border_width = 2
                
            # Draw slot background
            pygame.draw.rect(screen, (60, 60, 60), rect)
            pygame.draw.rect(screen, border_color, rect, border_width)
            
            # Draw item if present
            item = self.slots[i]
            if item:
                item.draw_icon(screen, rect.x + 4, rect.y + 4, HOTBAR_SLOT_SIZE - 8)
            
            # Draw slot number
            font = pygame.font.Font(None, 20)
            if i < 9:
                text = str(i + 1)
            elif i == 9:
                text = "0"
            elif i == 10:
                text = "-"
            else:  # i == 11
                text = "="
                
            text_surface = font.render(text, True, (200, 200, 200))
            screen.blit(text_surface, (rect.x + 2, rect.y + 2))