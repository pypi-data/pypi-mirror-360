import pygame
import os

from ..assets import GAME_ASSETS_BASE


class Drawable(pygame.sprite.Sprite):
    def __init__(self, width, height, color, image_name=""):
        super().__init__()

        self.width = width
        self.height = height
        self.color = color
        self.use_collider = True

        self.image = pygame.Surface([self.width, self.height])
        pygame.draw.rect(self.image, self.color, [0, 0, self.width, self.height])
        if image_name != "":
            image = pygame.image.load(os.path.join(GAME_ASSETS_BASE, image_name))
            image = pygame.transform.scale(image, (self.width, self.height))
            self.image.blit(image, self.image.get_rect())

        self.rect = self.image.get_rect()
        self.collider = self.rect.copy()

    def update_position(self, coordinates):
        self.rect.x = coordinates[0]
        self.rect.y = coordinates[1]
        self.collider.x = coordinates[0]
        self.collider.y = coordinates[1]
