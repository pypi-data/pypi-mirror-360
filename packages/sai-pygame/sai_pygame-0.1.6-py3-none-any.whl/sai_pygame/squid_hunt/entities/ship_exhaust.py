import math
import pygame

from sai_pygame.utils.animation import AnimationBase
from ..constants.config import SHIP_SIZE


class ShipExhaust(AnimationBase):
    def __init__(self, ship, sprites, position, size=(95, 10)):
        super().__init__(sprites, position, size, 2, [5, 5])
        x_offset = (size[0] * 0.25) + SHIP_SIZE * 0.5
        y_offset = SHIP_SIZE * 0.4

        # triangle offset between center of ship and center of flame
        # pos_offset is the hypotenuse of this triangle
        # pos_angle_offset is the angle of this hypotenuse
        self.pos_offset = math.sqrt(x_offset**2 + y_offset**2)
        self.pos_angle_offset = math.atan(y_offset / x_offset)

    def sync_with_ship(self, ship):
        rotated_image = pygame.transform.rotate(self.base_image, ship.angle)
        self.rect = rotated_image.get_rect(
            center=self.image.get_rect(
                center=(self.sizes[0] / 2, self.sizes[1] / 2)
            ).center
        )
        self.image = rotated_image

        x = ship.center_pos[0] - self.pos_offset * math.cos(
            math.radians(ship.angle) + self.pos_angle_offset
        )
        y = ship.center_pos[1] + self.pos_offset * math.sin(
            math.radians(ship.angle) + self.pos_angle_offset
        )
        self.rect.center = (x, y)

    def update(self, ship):
        kill_bool = super().update(loop_bool=True)
        self.sync_with_ship(ship)

        return kill_bool
