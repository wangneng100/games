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



class BowItem(WeaponItem):
    """Bow weapon item"""
    def __init__(self, bow_obj, image=None):
        super().__init__("Bow", bow_obj, image)

