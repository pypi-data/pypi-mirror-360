import pygame
import os

from ..assets import GAME_ASSETS_BASE
from ..constants import SCREEN_HEIGHT, SCREEN_WIDTH, SHIP_SIZE, SHIP_MAX_ANGLE
from .ship_exhaust import ShipExhaust


class Ship(pygame.sprite.Sprite):
    def __init__(self, exhaust_sprites):
        super().__init__()
        self.x = 0
        self.y = 0
        self.center_pos = (0, 0)
        self.xspd = 0
        self.yspd = 0
        self.speed = 6
        self.rotspd = 4
        self.angle = 0

        self.img = pygame.image.load(os.path.join(GAME_ASSETS_BASE, "ship.png"))
        self.img = pygame.transform.scale(self.img, (SHIP_SIZE, SHIP_SIZE))
        self.image = pygame.transform.rotate(self.img, self.angle)

        self.rect = pygame.Rect(100, 100, SHIP_SIZE, SHIP_SIZE)
        self.exhaust = ShipExhaust(self, exhaust_sprites, (0, 0))

    def reset(self):
        self.x = SCREEN_WIDTH / 4 - SHIP_SIZE / 2
        self.y = SCREEN_HEIGHT / 2 - SHIP_SIZE / 2
        self.angle = 0
        self.yspd = 0
        self.xspd = 0

    def rot_center(self, image, angle):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect().center)
        self.center_pos = (new_rect.center[0] + self.x, new_rect.center[1] + self.y)
        self.rect.x = new_rect.x + self.x
        self.rect.y = new_rect.y + self.y
        self.image = rotated_image

    def rotate_ship(self, angle):
        prev_angle = self.angle
        self.angle += angle
        if self.angle >= SHIP_MAX_ANGLE and self.angle <= 360 - SHIP_MAX_ANGLE:
            self.angle = prev_angle

    def update(self):
        self.angle %= 360
        self.x = max(0, min(self.x + self.xspd, SCREEN_WIDTH - SHIP_SIZE))
        self.y = max(0, min(self.y + self.yspd, SCREEN_HEIGHT - SHIP_SIZE))
        self.rot_center(self.img, self.angle)
        self.exhaust.update(self)
