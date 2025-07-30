import pygame

from .map import switch_assets


class Switch(pygame.sprite.Sprite):
    def __init__(self, sprites, group, size):
        super().__init__()
        self.group = group
        self.image = pygame.transform.scale(sprites[switch_assets[group]], (size, size))
        self.rect = self.image.get_rect()
        self.collider = self.rect.copy()

    def update_position(self, coordinates):
        self.rect.x = coordinates[0]
        self.rect.y = coordinates[1]
        self.collider.x = coordinates[0]
        self.collider.y = coordinates[1]
