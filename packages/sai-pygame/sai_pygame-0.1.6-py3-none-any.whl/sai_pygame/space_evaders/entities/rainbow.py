import os
import pygame

from ..assets import GAME_ASSETS_BASE


class Rainbow(pygame.sprite.Sprite):
    def __init__(self, x, y, image, lane, game, isStar=False):
        super().__init__()
        self.x = x
        self.y = y
        self.w = image.get_width()
        self.h = image.get_height()
        self.lane = lane
        self.game = game
        self.image = image
        self.rect = pygame.Rect(x, y, self.w, self.h)
        if not isStar:
            for i in range(3):
                startype = game.np_random.integers(1, 4)
                starx = game.np_random.integers(self.x + 10, self.x + self.w - 10)
                stary = game.np_random.integers(self.y + 15, self.y + self.h - 15)
                star = pygame.image.load(
                    os.path.join(
                        GAME_ASSETS_BASE, "rainbow/stars " + str(startype) + ".png"
                    )
                )
                starsprite = Rainbow(starx, stary, star, lane, game, True)
                game.all_sprites_list.add(starsprite)

    def update(self):
        self.y += self.game.speeds[self.lane]
        self.rect.x = self.x
        self.rect.y = self.y
        if self.rect.y > self.game.screen_height:
            self.game.all_sprites_list.remove(self)
