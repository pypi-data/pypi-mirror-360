import pygame
from ..constants import SCREEN_WIDTH


class Wall(pygame.sprite.Sprite):
    def __init__(self, wall_sprites, x, y, w, h, game):
        super().__init__()
        self.wall_sprites = wall_sprites
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.xspd = -3
        self.yspd = 0
        self.game = game
        self.image = pygame.Surface([w, h])
        self.image.fill((0, 0, 255))

        self.image = self.wall_sprites[0]
        self.image = pygame.transform.scale(self.image, (self.w, self.h))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.rect.x = self.rect.x + self.xspd
        self.rect.y = self.rect.y + self.yspd

        if self.rect.x > SCREEN_WIDTH * 0.66:
            self.image = self.wall_sprites[0]
        elif self.rect.x > SCREEN_WIDTH * 0.33:
            self.image = self.wall_sprites[1]
        else:
            self.image = self.wall_sprites[2]

        self.image = pygame.transform.scale(self.image, (self.w, self.h))

        if self.rect.x < 0 - self.w:
            self.game.walls_to_remove.add(self)
