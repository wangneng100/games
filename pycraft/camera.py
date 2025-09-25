import pygame

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.lerp_factor = 0.1

    def apply(self, entity_rect):
        return entity_rect.move(self.camera.topleft)

    def apply_point(self, point):
        return (point[0] + self.camera.left, point[1] + self.camera.top)

    def update(self, target_rect, mouse_pos):
        target_x = -target_rect.centerx + int(self.width / 2)
        target_y = -target_rect.centery + int(self.height / 2)

        mouse_offset_x = (mouse_pos[0] - self.width / 2) * 0.2
        mouse_offset_y = (mouse_pos[1] - self.height / 2) * 0.2

        target_x -= mouse_offset_x
        target_y -= mouse_offset_y

        new_x = self.camera.x + (target_x - self.camera.x) * self.lerp_factor
        new_y = self.camera.y + (target_y - self.camera.y) * self.lerp_factor
        
        self.camera = pygame.Rect(new_x, new_y, self.width, self.height)

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.camera.width = width
        self.camera.height = height
