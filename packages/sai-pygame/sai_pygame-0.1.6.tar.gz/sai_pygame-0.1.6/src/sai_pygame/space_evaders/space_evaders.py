import pygame
import numpy as np
import os

from gymnasium.spaces import Discrete, Box

from sai_pygame.utils.sprites import load_sprites_from_separate_files
from sai_pygame.utils.env import ArenaXGameBase
from sai_pygame.utils.colors import BLACK

from .entities.ship import Ship
from .entities.asteroid import Asteroid
from .objects.text import Text
from .entities.rainbow import Rainbow
from .assets import GAME_ASSETS_BASE

from .constants.config import (
    FRAMERATE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHIP_SIZE,
)

ACTION_MAPPING = {
    "left": (pygame.K_a, 1),
    "right": (pygame.K_d, 2),
}


class SpaceEvadersEnv(ArenaXGameBase):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": FRAMERATE,
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
        "engine": "pygame",
        "reward_functions": [
            "classic",
            "minimum_lane_change",
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
            game_name="Space Evaders - ArenaX Labs",
            action_mapping=ACTION_MAPPING,
            seed=seed,
            **kwargs,
        )
        # initialize game assets
        self.all_sprites_list = pygame.sprite.LayeredUpdates()
        self.speedinterval = self.time
        self.TIME_LIMIT = 60
        self.ASTEROID_INTERVAL = 100
        self.SHIP_SIZE = SHIP_SIZE
        self.slowest = 4
        self.fastest = 6
        self.maxspeed = 15
        self.speeds = [
            self.np_random.integers(self.slowest, self.fastest),
            self.np_random.integers(self.slowest, self.fastest),
            self.np_random.integers(self.slowest, self.fastest),
        ]
        ship_sprites = load_sprites_from_separate_files(
            "{}/ship/ship".format(GAME_ASSETS_BASE), 3
        )
        self.time_text = Text(
            self.screen_width / 2, 30, str(round(self.time, 2)), 30, self
        )
        self.rainbows = []
        self.bg = pygame.image.load(os.path.join(GAME_ASSETS_BASE, "background.png"))
        self.rainbow = pygame.image.load(
            os.path.join(GAME_ASSETS_BASE, "rainbow/rainbow.png")
        )
        self.rainbowsec = pygame.image.load(
            os.path.join(GAME_ASSETS_BASE, "rainbow/rainbow section.png")
        )
        self.rainbowsec = pygame.transform.scale(
            self.rainbowsec, (self.rainbowsec.get_width(), self.rainbowsec.get_height())
        )
        self.dead = False
        self.lastrainbows = [None] * 3
        self.asteroids = [[] for i in range(3)]
        self.nextAsteroid = self.np_random.integers(0, 2)
        self.gridrows = 6
        self.gridcolumns = 3
        for i in range(3):
            x = (i + 1) * (self.screen_width) / 4
            rainbow = Rainbow(
                x - self.rainbowsec.get_width() / 2,
                -self.rainbowsec.get_height(),
                self.rainbowsec,
                i,
                self,
            )
            self.lastrainbows[i] = rainbow
            self.all_sprites_list.add(rainbow)
        x = SCREEN_WIDTH / 2 - SHIP_SIZE / 2
        y = SCREEN_HEIGHT * 3 / 4 - SHIP_SIZE / 2
        self.ship = Ship(ship_sprites, x, y)
        self.all_sprites_list.add(self.ship)

        # reset game
        self.reset()

        # define action and observation space
        self.action_space = Discrete(3)
        self.observation_space = Box(
            low=np.array([-1, 0, 0, 0] + [0] * (self.gridcolumns * self.gridrows)),
            high=np.array([1] * 4 + [1] * (self.gridcolumns * self.gridrows)),
            dtype=np.float32,
        )

        # initialize reward function
        self.reward_functions = {
            "classic": self._classic_reward,
            "minimum_lane_change": self._minimum_lane_change_reward,
        }
        self.reward_function = self.reward_functions[reward_function]
        assert reward_function in self.reward_functions, (
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
        self.speeds = [
            self.np_random.integers(self.slowest, self.fastest),
            self.np_random.integers(self.slowest, self.fastest),
            self.np_random.integers(self.slowest, self.fastest),
        ]
        self.all_sprites_list = pygame.sprite.LayeredUpdates()
        self.asteroids = [[] for i in range(3)]
        for i in range(3):
            x = (i + 1) * (self.screen_width) / 4
            rainbow = Rainbow(
                x - self.rainbowsec.get_width() / 2,
                -self.rainbowsec.get_height(),
                self.rainbowsec,
                i,
                self,
            )
            self.lastrainbows[i] = rainbow
            self.all_sprites_list.add(rainbow)
        for i in range(3):
            x = (i + 1) * (self.screen_width) / 4
            r = Rainbow(x - self.rainbow.get_width() / 2, -80, self.rainbow, i, self)
            self.all_sprites_list.add(r)
        self.ship.reset()
        self.all_sprites_list.add(self.ship)
        self.nextAsteroid = self.np_random.integers(0, 2)
        self.dead = False
        self.speedinterval = self.time

        observation = self.get_observation()

        info = {
            "timestep": self.frame,
            "asteroids": len([a for i in self.asteroids for a in i]),
        }

        return observation, info

    def step(self, action):
        """
        Perform one step of the game, then extract the observation.
        """
        self.update(action)
        super().step()

        observation = self.get_observation()
        done = self.done
        truncated = self.truncated
        reward = self.get_reward()

        info = {
            "timestep": self.frame,
            "asteroids": len([a for i in self.asteroids for a in i]),
        }

        return observation, reward, done, truncated, info

    def update(self, action):
        """
        Move the game state forward one frame, given an action for the paddle(s).
        """
        # game loop goes here
        if self.time - self.speedinterval > 10:
            for i in range(3):
                self.speeds[i] = min(self.maxspeed, self.speeds[i] + 1)
            self.speedinterval = self.time

        self.all_sprites_list.update()
        if action == 1:
            self.ship.move(-1)
        if action == 2:
            self.ship.move(1)

        for i in range(3):
            if self.lastrainbows[i] is None or self.lastrainbows[i].y > -self.speeds[i]:
                x = (i + 1) * (self.screen_width) / 4
                if self.np_random.integers(1, 9) > 1 and i == self.nextAsteroid:
                    cluster = self.np_random.integers(1, 7)
                    astrImg = pygame.image.load(
                        os.path.join(
                            GAME_ASSETS_BASE,
                            "asteroids/asteroid cluster " + str(cluster) + ".png",
                        )
                    )
                    width = astrImg.get_width()
                    height = astrImg.get_height()
                    asteroid = Asteroid(
                        x - width / 2, -height, width, height, astrImg, i, self
                    )
                    self.asteroids[i].append(asteroid)
                    # make sure generated asteroid won't trap the ship by either keeping middle or both side lanes free
                    if self.checkBlockade():
                        self.asteroids[i].remove(asteroid)
                        rainbow = Rainbow(
                            x - self.rainbowsec.get_width() / 2,
                            -self.rainbowsec.get_height(),
                            self.rainbowsec,
                            i,
                            self,
                        )
                        self.lastrainbows[i] = rainbow
                        self.all_sprites_list.add(rainbow)
                        self.all_sprites_list.move_to_back(rainbow)
                        continue
                    # print([len(i) for i in self.asteroids])
                    self.nextAsteroid = self.np_random.integers(0, 2)
                    self.all_sprites_list.add(asteroid)
                    self.lastrainbows[i] = asteroid

                else:
                    rainbow = Rainbow(
                        x - self.rainbowsec.get_width() / 2,
                        -self.rainbowsec.get_height(),
                        self.rainbowsec,
                        i,
                        self,
                    )
                    self.lastrainbows[i] = rainbow
                    self.all_sprites_list.add(rainbow)
                    self.all_sprites_list.move_to_back(rainbow)

        self.check_collisions()
        if self.TIME_LIMIT - self.time <= 0:
            self.truncated = True
        self.time_text.update("TIME: " + str(round(self.time, 1)))

    def check_collisions(self):
        for j in self.asteroids:
            for i in j:
                if pygame.Rect(
                    self.ship.rect.x,
                    self.ship.rect.y,
                    self.ship.image.get_width(),
                    self.ship.image.get_height(),
                ).colliderect(i.rect):
                    self.done = True
                    self.dead = True
                    return

    def render(self):
        """
        Render the game based on the mode.
        """
        # draw everything to the screen
        self.screen.fill(BLACK)
        self.screen.blit(self.bg, (0, 0))
        self.all_sprites_list.move_to_front(self.ship)
        self.all_sprites_list.draw(self.screen)
        self.screen.blit(
            self.time_text.image,
            (
                self.time_text.x - self.time_text.image.get_width() / 2,
                self.time_text.y - self.time_text.image.get_height() / 2,
            ),
        )
        return super().render()

    def get_observation(self):
        """
        Return the current observation from the game state.
        """
        # use the game state to output an array in the format of your observation space
        ship_position = ((self.ship.x + SHIP_SIZE / 2) - self.screen_width / 2) / (
            self.screen_width / 4
        )
        ast_casts = []
        # closest asteroids to the ship in each lane
        # for i in self.asteroids:
        #     if len(i) > 0:
        #         ast_casts.append(1 + (i[0].y - (self.ship.y + SHIP_SIZE)) / (self.ship.y + SHIP_SIZE + i[0].h))
        #     else:
        #         ast_casts.append(0)
        self.normalspeeds = [
            (i - self.slowest) / (self.maxspeed - self.slowest) for i in self.speeds
        ]
        columns = self.gridcolumns
        rows = self.gridrows
        intersections = [[0 for i in range(columns)] for j in range(rows)]
        count = 0
        asteroids = [a for i in self.asteroids for a in i]
        # for a in asteroids:
        #     pygame.draw.rect(self.screen, RED, a.rect)

        for i in range(rows):
            for j in range(columns):
                cell = pygame.Rect(
                    SCREEN_WIDTH / columns * j,
                    SCREEN_HEIGHT / rows * i,
                    SCREEN_WIDTH / columns,
                    SCREEN_HEIGHT / rows,
                )
                for a in asteroids:
                    if pygame.Rect.clipline(
                        a.rect,
                        cell.centerx,
                        SCREEN_HEIGHT / rows * i,
                        cell.centerx,
                        SCREEN_HEIGHT / rows * (i + 1),
                    ):
                        intersections[i][j] = 1
                        count += 1
                # pygame.draw.rect(self.screen, RED if intersections[i][j] else BLACK, cell, 3)

        flat_intersections = [j for i in intersections for j in i]
        arr = [ship_position] + self.normalspeeds + flat_intersections
        return np.array(arr, dtype=np.float32)

    def get_reward(self):
        """
        Return the reward from the current game state.
        """
        return self.reward_function()

    def _classic_reward(self):
        if self.dead:
            return -5

        return 0.01

    def _minimum_lane_change_reward(self):
        if self.dead:
            return -5

        lane_changes = abs(self.ship.previous_lane - self.ship.lane)
        lane_change_penalty = -0.1 * lane_changes

        survival_reward = 0.01

        return lane_change_penalty + survival_reward

    def checkBlockade(self):
        delay = SHIP_SIZE * 2 / self.framerate / self.slowest
        for i in range(2):
            # print("i:", i)
            for j in self.asteroids[i]:
                # print("j:", self.asteroids[i].index(j))
                for k in range(i + 1, 3):
                    # print("k:", i)
                    for l in self.asteroids[k]:
                        # print("l:", self.asteroids[k].index(l))
                        # print(str(round(j.start, 1)),  str(round(j.end, 1)), str(round(l.start, 1)), str(round(l.end, 1)))
                        if not (j.start > l.end + delay or j.end + delay < l.start):
                            if i == 1 or k == 1:
                                return True
        return False
