import pygame

from sai_pygame.utils.animation import AnimationBase

from ..constants import SCREEN_HEIGHT, SCREEN_WIDTH, SHIP_SIZE


class Ship(AnimationBase):
    def __init__(self, ship_sprites, x, y):
        super().__init__(ship_sprites, (x, y), (SHIP_SIZE, SHIP_SIZE), 3, [5, 5, 5])
        self.x = 0
        self.y = 0
        self.center_pos = (0, 0)
        self.xspd = 0
        self.yspd = 0
        self.speed = 10
        self.angle = 0
        self.lane = 2
        self.previous_lane = 2
        self.moving = None

        self.rect = pygame.Rect(100, 100, SHIP_SIZE, SHIP_SIZE)

    def reset(self):
        self.x = SCREEN_WIDTH / 2 - SHIP_SIZE / 2
        self.y = SCREEN_HEIGHT * 3 / 4 - SHIP_SIZE / 2
        self.lane = 2
        self.previous_lane = 2

    def update(self):
        if self.moving is not None:
            if (
                abs((self.x + SHIP_SIZE / 2) - ((self.moving) * SCREEN_WIDTH / 4))
                <= self.speed
            ):
                self.x = (self.moving) * SCREEN_WIDTH / 4 - SHIP_SIZE / 2
                self.previous_lane = self.lane
                self.lane = self.moving
                self.moving = None
                self.xspd = 0
            else:
                self.xspd = (self.moving - self.lane) * self.speed

        self.x += self.xspd
        self.y += self.yspd
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        return super().update(loop_bool=True)

    def move(self, dir):
        if 1 <= self.lane + dir <= 3:
            self.moving = self.lane + dir
