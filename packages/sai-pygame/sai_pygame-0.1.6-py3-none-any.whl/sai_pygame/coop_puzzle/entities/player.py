import pygame
from sai_pygame.utils.animation import AnimationBase

from .map import TILE_SIZE


def get_player_tile(rect):
    tile_x = rect.center[0] // TILE_SIZE
    tile_y = rect.center[1] // TILE_SIZE
    return tile_y, tile_x


class Player(AnimationBase):
    def __init__(
        self,
        all_sprites,
        sprite_group,
        size,
        position,
        screen_height,
        speed,
        wall_colliders,
        switch_colliders,
        door_colliders,
        floor,
        goal_colliders,
        game,
    ):
        super().__init__(all_sprites[sprite_group], position, size, 2, [12, 12])

        self.direction_to_sizes = {
            "down": {"aspect": (83, 95), "base": size * 0.95},
            "side": {"aspect": (98, 70), "base": size * 0.75},
            "idle": {"aspect": (91, 83), "base": size * 0.85},
            "up": {"aspect": (83, 105), "base": size},
        }

        self.rect = self.image.get_rect()
        self.collider = self.rect.copy()
        self.all_sprites = all_sprites
        self.animation_direction = {"key": sprite_group, "invert": False}

        self.screen_height = screen_height
        self.speed = speed
        self.wall_colliders = wall_colliders
        self.switch_colliders = switch_colliders
        self.door_colliders = door_colliders
        self.floor = floor
        self.goal_colliders = goal_colliders
        self.game = game

        self.on_switch = False
        self.on_goal = False
        self.moving = False
        self.prev_moving = True
        self.prev_horizontal_invert = False

    def update_position(self, coordinates):
        self.rect.x = coordinates[0]
        self.rect.y = coordinates[1]
        self.collider.x = coordinates[0]
        self.collider.y = coordinates[1]

    def move(self, horizonalAxis, verticleAxis):
        dir = pygame.math.Vector2(horizonalAxis, verticleAxis)

        self.moving = True
        if horizonalAxis != 0:
            self.prev_horizontal_invert = horizonalAxis == -1
            self.animation_direction = {"key": "side", "invert": horizonalAxis == -1}
        elif verticleAxis == 1:
            self.animation_direction = {"key": "down", "invert": False}
        elif verticleAxis == -1:
            self.animation_direction = {"key": "up", "invert": False}
        else:
            self.moving = False

        # TODO: smooth acceleration
        if dir.length() != 0:
            dir.scale_to_length(self.speed)
            self.collider.x = self.rect.x + dir.x
            self.collider.y = self.rect.y + dir.y
            gate_collision = self.collider.collidelist(self.door_colliders)
            if (
                (gate_collision != -1 and self.game.gates[gate_collision].use_collider)
                or self.collider.collidelist(self.wall_colliders) != -1
                or not self.floor.contains(self.collider)
            ):
                self.collider.x = self.rect.x
                self.collider.y = self.rect.y
                self.game.player_collided(gate_collision != -1)
            else:
                self.rect.x += dir.x
                self.rect.y += dir.y
                switch_collision = self.collider.collidelist(self.switch_colliders)
                if switch_collision != -1:
                    if not self.on_switch:
                        self.game.update_switch(
                            self.game.switches[switch_collision].group
                        )
                        self.on_switch = True
                elif self.on_switch:
                    self.on_switch = False
                goal_collision = self.collider.collidelist(self.goal_colliders)
                if goal_collision != -1:
                    if not self.on_goal:
                        self.on_goal = True
                        self.game.player_reached_goal()
                elif self.on_goal:
                    self.on_goal = False

    def get_new_size(self, direction_key="idle"):
        new_sizes = self.direction_to_sizes[direction_key]
        aspect = new_sizes["aspect"][0] / new_sizes["aspect"][1]
        self.base_size = new_sizes["base"]
        self.invert_axis["x"] = self.animation_direction["invert"]
        return (self.base_size * aspect, self.base_size)

    def update(self):
        if self.moving:
            self.sprites = self.all_sprites[self.animation_direction["key"]]
            self.sizes = self.get_new_size(self.animation_direction["key"])
            super().update(True)
            self.prev_moving = True
        elif self.prev_moving:
            self.image = self.all_sprites["idle"]
            self.animation_direction["invert"] = self.prev_horizontal_invert
            self.sizes = self.get_new_size()
            self.image = pygame.transform.scale(
                self.image, (self.sizes[0], self.sizes[1])
            )
            self.image = pygame.transform.flip(
                self.image, self.invert_axis["x"], self.invert_axis["y"]
            )
            self.prev_moving = False

    def reset(self):
        self.reset_animation()
        self.on_goal = False
        self.on_switch = False
        self.moving = False
        self.prev_moving = True
        self.prev_horizontal_invert = False
