import pygame
import numpy as np
import os

from sai_pygame.utils.env import ArenaXGameBase
from sai_pygame.utils.sprites import load_sprites_from_separate_files
from sai_pygame.utils.colors import RED, BLACK

from gymnasium.spaces import Discrete, Box

from .assets import GAME_ASSETS_BASE
from .entities.bullet import Bullet
from .entities.ship import Ship
from .entities.squid import Squid
from .objects.text import Text
from .entities.wall import Wall

from .constants.config import (
    FRAMERATE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHIP_SIZE,
    BACKGROUND_OPACITY,
    BACKGROUND_SPEED,
    BACKGROUND_HEIGHT,
    BACKGROUND_WIDTH,
    SHIP_MAX_ANGLE,
)


ACTION_MAPPING = {
    "up": (pygame.K_w, 1),
    "down": (pygame.K_s, 2),
    "rotate_cc": (pygame.K_a, 3),
    "rotate_c": (pygame.K_d, 6),
    "shoot": (pygame.K_SPACE, 9),
}


class SquidHuntEnv(ArenaXGameBase):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": FRAMERATE,
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
        "engine": "pygame",
        "reward_functions": [
            "classic",
            "highest_kill_count",
            "precision_shooting",
            "ammo_efficiency",
            "time_survival",
        ],
    }

    def __init__(
        self,
        render_mode="rgb_array",
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        framerate=FRAMERATE,
        seed=None,
        reward_function="classic",
        **kwargs,
    ):
        super().__init__(
            width=width,
            height=height,
            framerate=framerate,
            render_mode=render_mode,
            game_name="Squid Hunt - ArenaX Labs",
            action_mapping=ACTION_MAPPING,
            seed=seed,
            **kwargs,
        )
        # initialize game assets
        self.all_sprites_list = pygame.sprite.Group()

        self.TIME_LIMIT = 30
        self.WALL_INTERVAL = 200
        self.SQUID_INTERVAL = 100
        self.AMMO_INTERVAL = 100
        self.MAX_AMMO = 30
        self.INITIAL_AMMO = 10
        # can be "random", "up", or "down"
        self.ENEMYSPAWN = "random"
        self.WALL_SPAWN = True

        self.genY = 0 if self.ENEMYSPAWN == "down" else self.screen_height - 60
        self.SHIP_SIZE = SHIP_SIZE
        self.score = 0
        self.ammo = self.INITIAL_AMMO

        self.city_x_position = 0
        self.city_scroll_speed = BACKGROUND_SPEED

        darkening_surface = pygame.Surface(
            (BACKGROUND_WIDTH, BACKGROUND_HEIGHT), pygame.SRCALPHA
        )
        darkening_surface.fill((0, 0, 0, 255 - BACKGROUND_OPACITY))
        self.city = pygame.image.load(os.path.join(GAME_ASSETS_BASE, "city.jpg"))
        self.city = pygame.transform.scale(
            self.city, (BACKGROUND_WIDTH, BACKGROUND_HEIGHT)
        )
        self.city.blit(darkening_surface, (0, 0))

        self.walls_to_remove = set()
        self.squids_to_remove = set()
        self.bullets_to_remove = set()

        exhaust_sprites = load_sprites_from_separate_files(
            "{}/ship-exhaust/ship-exhaust".format(GAME_ASSETS_BASE), 2
        )
        self.ship = Ship(exhaust_sprites)
        self.all_sprites_list.add(self.ship)

        self.time_text = Text(
            self.screen_width / 2,
            30,
            str(round(self.TIME_LIMIT - self.time, 2)),
            30,
            self,
        )
        self.ammo_text = Text(
            self.screen_width / 3,
            self.screen_height - 30,
            "BULLETS: " + str(self.ammo),
            30,
            self,
        )
        self.score_text = Text(
            self.screen_width / 3 * 2,
            self.screen_height - 30,
            "SCORE: " + str(self.score),
            30,
            self,
        )

        self.wall_sprites = load_sprites_from_separate_files(
            "{}/wall/wall".format(GAME_ASSETS_BASE), 3
        )
        self.projectile_sprites = load_sprites_from_separate_files(
            "{}/projectile/projectile".format(GAME_ASSETS_BASE), 3
        )
        self.squid_sprites = {
            "ORANGE": load_sprites_from_separate_files(
                "{}/squids/squid--orange-".format(GAME_ASSETS_BASE), 3
            ),
            "PINK": load_sprites_from_separate_files(
                "{}/squids/squid--pink-".format(GAME_ASSETS_BASE), 3
            ),
        }
        self.explosion_sprites = load_sprites_from_separate_files(
            "{}/explosion/explosion".format(GAME_ASSETS_BASE), 3
        )

        self.killed = False
        self.shot = False
        self.dead = False
        self.prevY = self.ship.y
        self.shot_action = False
        self.closest_hazard = 9999

        # reset game
        self.reset()

        # define action and observation space
        self.action_space = Discrete(10)
        self.observation_space = Box(
            low=np.array([-1] * 23), high=np.array([1] * 23), dtype=np.float32
        )

        # initialize reward function
        self.reward_functions = {
            "classic": self._classic_reward,
            "highest_kill_count": self._highest_kill_count_reward,
            "precision_shooting": self._precision_shooting_reward,
            "ammo_efficiency": self._ammo_efficiency_reward,
            "time_survival": self._time_survival_reward,
        }
        self.reward_function = self.reward_functions[reward_function]
        assert self.reward_function is not None, (
            f"Invalid reward function: {reward_function}"
        )

        # get initial state
        self.init_obs = self.get_observation()

    def reset(self, **kwargs):
        """
        Reset the game to its initial state.
        """
        super().reset(**kwargs)
        # reset the game environment back to the initial state
        self.genY = 0 if self.ENEMYSPAWN == "down" else self.screen_height - 60
        self.walls = set()
        self.bullets = set()
        self.squids = set()

        self.all_sprites_list = pygame.sprite.Group()
        self.all_sprites_list.add(self.ship)
        self.ship.reset()

        self.ammo = self.INITIAL_AMMO
        self.score = 0
        self.killed = False
        self.shot = False
        self.shot_action = False
        self.dead = False
        self.combo_streak = 0
        self.closest_hazard = self.get_nearest_hazard()
        self.prevY = self.ship.y

        observation = self.get_observation()
        info = self.get_info()
        return observation, info

    def get_reward(self):
        """
        Return the reward from the current game state.
        """
        return self.reward_function()

    def get_info(self):
        """
        Return the info from the current game state.
        """
        info = {
            "timestep": self.frame,
            "time": self.time,
            "num_walls": len(self.walls),
            "num_squids": len(self.squids),
            "num_bullets": len(self.bullets),
            "shotBullet": self.shot,
            "failedShot": self.shot_action,
            "bullets": len(self.bullets),
            "squids": len(self.squids),
            "approaching_danger": self.closest_hazard > self.get_nearest_hazard(),
            "approaching_edge": (
                self.screen_height / 5 > self.prevY > self.ship.y
                or self.screen_height * 0.8 - self.ship.image.get_height()
                < self.prevY
                < self.ship.y
            ),
        }

        self.closest_hazard = self.get_nearest_hazard()
        self.prevY = self.ship.y
        return info

    def render(self):
        """
        Render the game based on the mode.
        """
        # draw everything to the screen
        self.screen.fill(BLACK)
        self.screen.blit(self.city, (self.city_x_position, -100))
        if self.city_x_position <= -self.screen_width + self.screen_width:
            self.screen.blit(
                self.city, (self.city_x_position + self.screen_width, -100)
            )
        self.all_sprites_list.draw(self.screen)
        self.screen.blit(self.ship.exhaust.image, self.ship.exhaust.rect)
        self.screen.blit(
            self.ammo_text.image,
            (
                self.ammo_text.x - self.ammo_text.image.get_width() / 2,
                self.ammo_text.y - self.ammo_text.image.get_height() / 2,
            ),
        )
        self.screen.blit(
            self.time_text.image,
            (
                self.time_text.x - self.time_text.image.get_width() / 2,
                self.time_text.y - self.time_text.image.get_height() / 2,
            ),
        )
        self.screen.blit(
            self.score_text.image,
            (
                self.score_text.x - self.score_text.image.get_width() / 2,
                self.score_text.y - self.score_text.image.get_height() / 2,
            ),
        )

        return super().render()

    def step(self, action):
        """
        Move the game state forward one frame, given an action for the paddle(s).
        """
        self.update(action)
        super().step()

        observation = self.get_observation()
        done = self.done
        truncated = done
        reward = self.get_reward()
        info = self.get_info()

        return observation, reward, done, truncated, info

    def update(self, action):
        """
        Update the game state based on the action.
        """
        self.killed = False
        self.shot = False
        self.shot_action = False
        self.all_sprites_list.update()

        if action % 3 == 0:
            self.ship.yspd = 0
        if action % 3 == 1:
            self.ship.yspd = -self.ship.speed
        if action % 3 == 2:
            self.ship.yspd = self.ship.speed
        if action >= 3 and action < 6:
            self.ship.rotate_ship(self.ship.rotspd)
        if action >= 6 and action < 9:
            self.ship.rotate_ship(-self.ship.rotspd)
        if action == 9:
            if self.ammo > 0:
                bullet = Bullet(self.projectile_sprites, (20, 20), self)
                self.bullets.add(bullet)
                self.all_sprites_list.add(bullet)
                self.all_sprites_list.remove(self.ship)
                self.all_sprites_list.add(self.ship)
                self.ammo -= 1
                self.shot = True
            else:
                self.shot_action = True

        if self.frame % self.WALL_INTERVAL == 0 and self.WALL_SPAWN:
            y = 0
            if self.ENEMYSPAWN == "random":
                y = self.np_random.integers(0, self.screen_height - 100)
            else:
                y = self.genY
            wall = Wall(self.wall_sprites, self.screen_width, y, 20, 100, self)
            self.genY = (
                self.genY + (50 if self.ENEMYSPAWN == "down" else -50)
            ) % self.screen_height
            self.walls.add(wall)
            self.all_sprites_list.add(wall)
        if self.frame % self.SQUID_INTERVAL == 0:
            y = 0
            if self.ENEMYSPAWN == "random":
                y = self.np_random.integers(0, self.screen_height - 100)
            else:
                y = self.genY
            squid_color = self.np_random.choice(["ORANGE", "PINK"])
            squid = Squid(
                self.squid_sprites[squid_color], self.screen_width, y, 115, 40, self
            )
            self.genY = (
                self.genY + (50 if self.ENEMYSPAWN == "down" else -50)
            ) % self.screen_height
            self.squids.add(squid)
            self.all_sprites_list.add(squid)
        if self.frame % self.AMMO_INTERVAL == 0 and self.ammo < self.MAX_AMMO:
            self.ammo += 1
        self.check_collisions()
        self.clear_sprites()
        self.time_text.update("TIME: " + str(round(self.TIME_LIMIT - self.time, 1)))
        self.ammo_text.update("BULLETS: " + str(self.ammo))
        self.score_text.update("SCORE: " + str(self.score))
        if self.TIME_LIMIT - self.time <= 0:
            self.done = True

        self.city_x_position -= self.city_scroll_speed
        if self.city_x_position <= -self.screen_width:
            self.city_x_position = 0

    def clear_sprites(self):
        for i in self.walls_to_remove:
            self.walls.remove(i)
            self.all_sprites_list.remove(i)
        self.walls_to_remove = set()
        for i in self.squids_to_remove:
            self.squids.remove(i)
            self.all_sprites_list.remove(i)
        self.squids_to_remove = set()
        for i in self.bullets_to_remove:
            self.bullets.remove(i)
            self.all_sprites_list.remove(i)
        self.bullets_to_remove = set()

    def check_collisions(self):
        for i in self.walls.union(self.squids):
            if pygame.Rect(
                self.ship.rect.x,
                self.ship.rect.y,
                self.ship.image.get_width(),
                self.ship.image.get_height(),
            ).colliderect(i.rect):
                self.done = True
                self.dead = True
                return

            for j in self.bullets:
                if i.rect.colliderect(j.rect):
                    if i in self.squids:
                        i.explode(self.explosion_sprites, (100, 100))
                        self.killed = True
                        self.score += 1
                    self.bullets_to_remove.add(j)
                    break

    def get_ray_distance(self, clip):
        buffer = 150
        dist = 1 - (clip - buffer) / (self.screen_width - buffer)
        if dist > 1:
            return -1
        return dist

    def get_observation(self):
        """
        Return the current observation from the game state.
        """
        # use the game state to output an array in the format of your observation space
        wall_casts = []
        squid_casts = []
        y = 25
        # horizontal rays that return the x coordinate of the leftmost intersecting wall and squid
        while y < self.screen_height:
            clipped = False
            for i in self.walls:
                clip = i.rect.clipline(0, y, self.screen_width, y)
                if clip != ():
                    pygame.draw.circle(self.screen, RED, clip[0], 3)
                    wall_casts.append(self.get_ray_distance(clip[0][0]))
                    clipped = True
                    break
            if not clipped:
                wall_casts.append(-1)
            clipped = False
            for i in self.squids:
                clip = i.rect.clipline(0, y, self.screen_width, y)
                if clip != ():
                    pygame.draw.circle(self.screen, RED, clip[0], 3)
                    squid_casts.append(self.get_ray_distance(clip[0][0]))
                    clipped = True
                    break
            if not clipped:
                squid_casts.append(-1)
            y += 50

        ship_position = ((self.ship.y + SHIP_SIZE / 2) / self.screen_height - 0.5) * 2
        ship_position /= 1 - SHIP_SIZE / self.screen_height

        if self.ship.angle > 180:
            angle_feature = (self.ship.angle - 360) / SHIP_MAX_ANGLE
        else:
            angle_feature = self.ship.angle / SHIP_MAX_ANGLE
        arr = (
            [ship_position, angle_feature, self.ammo / self.MAX_AMMO]
            + wall_casts
            + squid_casts
        )
        return np.array(arr, dtype=np.float32)

    def get_nearest_hazard(self):
        mini = 9999
        minx = 9999
        for i in self.squids.union(self.walls):
            proxx = (
                i.rect.x
                + i.image.get_width() / 2
                - self.ship.rect.x
                - self.ship.image.get_width() / 2
            )
            if 0 <= proxx < minx:
                prox = abs(
                    i.rect.y
                    + i.image.get_height() / 2
                    - self.ship.rect.y
                    - self.ship.image.get_height() / 2
                )
                mini = min(mini, prox)
                minx = (
                    i.rect.x
                    + i.image.get_width() / 2
                    - self.ship.rect.x
                    - self.ship.image.get_width() / 2
                )
        return mini

    def _classic_reward(self):
        reward = 0
        if self.killed:
            reward += 0.5
        if self.dead:
            reward -= 5
        return reward + 0.01

    def _highest_kill_count_reward(self):
        reward = 0
        if self.killed:
            reward += 1
        if self.shot and not self.killed:  # Missing a shot
            reward -= 0.01
        return reward + 0.01

    def _precision_shooting_reward(self):
        reward = 0
        if self.killed:
            self.combo_streak += 1
            reward += 0.5 * self.combo_streak
        elif self.shot and not self.killed:  # Missing a shot
            reward -= 0.05
            self.combo_streak = 0  # Reset combo
        return reward + 0.01

    def _ammo_efficiency_reward(self):
        reward = 0
        if self.killed:
            reward += 1
        if self.shot:  # Penalty for each shot fired
            reward -= 0.1
        return reward + 0.01

    def _time_survival_reward(self):
        reward = 0
        if self.dead:
            reward -= 5
        return reward + 0.01
