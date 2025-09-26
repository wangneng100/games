import pygame

class Item:
    """Base class for all items"""
    def __init__(self, name, item_type, image=None):
        self.name = name
        self.item_type = item_type  # "weapon", "tool", "consumable", etc.
        self.image = image
        
    def use(self, player, **kwargs):
        """Override in subclasses to define item behavior"""
        pass
        
    def draw_icon(self, screen, x, y, size):
        """Draw the item icon on screen"""
        if self.image:
            scaled_image = pygame.transform.scale(self.image, (size, size))
            screen.blit(scaled_image, (x, y))

class WeaponItem(Item):
    """Base class for weapon items"""
    def __init__(self, name, weapon_obj, image=None):
        super().__init__(name, "weapon", image)
        self.weapon = weapon_obj
        
    def use(self, player, **kwargs):
        """Equip this weapon"""
        return self.weapon

class SwordItem(WeaponItem):
    """Sword weapon item"""
    def __init__(self, staff_obj, image=None):
        super().__init__("Sword", staff_obj, image)

class BowItem(WeaponItem):
    """Bow weapon item"""
    def __init__(self, bow_obj, image=None):
        super().__init__("Bow", bow_obj, image)

class KnifeItem(WeaponItem):
    """Knife weapon item"""
    def __init__(self, knife_obj, image=None):
        super().__init__("Knife", knife_obj, image)
    
    def draw_icon(self, screen, x, y, size):
        """Draw knife icon 3x smaller but properly oriented in hotbar slot"""
        if self.image:
            # Make knife 3x smaller than slot size while maintaining aspect ratio
            knife_height = int(size * 0.33)  # 1/3 of slot height (3x smaller)
            knife_width = int(self.image.get_width() * (knife_height / self.image.get_height()))
            scaled_knife = pygame.transform.scale(self.image, (knife_width, knife_height))
            
            # Center the smaller knife in the slot
            draw_x = x + (size - knife_width) // 2
            draw_y = y + (size - knife_height) // 2
            
            screen.blit(scaled_knife, (draw_x, draw_y))