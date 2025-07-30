import math

from sai_pygame.utils.animation import AnimationBase

from ..constants.config import SHIP_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH


class Bullet(AnimationBase):
    def __init__(self, projectile_sprites, size, game):
        self.game = game
        x_offset = SHIP_SIZE * 0.5
        y_offset = SHIP_SIZE * 0.3
        self.pos_offset = math.sqrt(x_offset**2 + y_offset**2)
        self.pos_angle_offset = math.atan(y_offset / x_offset)

        x = game.ship.center_pos[0] + self.pos_offset * math.cos(
            math.radians(game.ship.angle) - self.pos_angle_offset
        )
        y = game.ship.center_pos[1] - self.pos_offset * math.sin(
            math.radians(game.ship.angle) - self.pos_angle_offset
        )

        super().__init__(projectile_sprites, (x, y), size, 3, [5, 5, 5])
        self.spd = 8
        self.xspd = 3
        self.yspd = 0
        self.rotation = self.game.ship.angle

    def update(self):
        self.xspd = math.cos(math.radians(self.rotation)) * self.spd
        self.yspd = math.sin(math.radians(self.rotation)) * -self.spd
        self.rect.x = self.rect.x + self.xspd
        self.rect.y = self.rect.y + self.yspd
        if (
            self.rect.x >= SCREEN_WIDTH
            or self.rect.x <= 0
            or self.rect.y >= SCREEN_HEIGHT
            or self.rect.y <= 0
        ):
            self.game.bullets_to_remove.add(self)

        return super().update(stay_on_last_frame=True)
