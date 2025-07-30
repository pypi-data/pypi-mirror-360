import random
import pygame

from sai_pygame.utils.animation import AnimationBase

from .squid_explosion import SquidExplosion


class Squid(AnimationBase):
    def __init__(self, squid_sprites, x, y, w, h, game):
        super().__init__(squid_sprites, (x, y), (w, h), 3, [5, 5, 5])
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.xspd = -5
        self.yspd = 0
        self.game = game

        self.image = random.choice(squid_sprites)
        self.image = pygame.transform.scale(self.image, (self.w, self.h))
        self.rect = pygame.Rect(x, y, w, h)

        self.explosion = None

    def update(self):
        self.rect.x = self.rect.x + self.xspd
        self.rect.y = self.rect.y + self.yspd
        if self.rect.x < 0 - self.w:
            self.game.squids_to_remove.add(self)

        return super().update(loop_bool=True)

    def explode(self, explosion_sprites, size):
        self.explosion = SquidExplosion(
            explosion_sprites,
            (self.rect.center[0], self.rect.center[1]),
            size,
            self.game,
        )
        self.game.all_sprites_list.add(self.explosion)
        self.game.squids_to_remove.add(self)
