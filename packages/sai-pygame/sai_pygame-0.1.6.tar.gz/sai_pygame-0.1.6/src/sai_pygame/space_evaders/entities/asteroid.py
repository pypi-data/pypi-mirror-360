import pygame


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image, lane, game):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.game = game
        self.lane = lane
        self.image = image
        self.rect = pygame.Rect(x, y, w, h)
        self.createTime = self.game.time
        self.start = (
            self.createTime
            + self.game.ship.y / self.game.speeds[self.lane] / self.game.framerate
        )
        self.end = (
            self.start + self.h / self.game.speeds[self.lane] / self.game.framerate
        )

    def update(self):
        self.y += self.game.speeds[self.lane]
        self.start = (
            self.createTime
            + self.game.ship.y / self.game.speeds[self.lane] / self.game.framerate
        )
        self.end = (
            self.start + self.h / self.game.speeds[self.lane] / self.game.framerate
        )
        if self.rect.y > self.game.screen_height:
            self.game.all_sprites_list.remove(self)
            self.game.asteroids[self.lane].remove(self)

        self.rect.x = self.x
        self.rect.y = self.y
