from typing import Optional

import pygame
import numpy as np
import gymnasium as gym

from sai_pygame.utils.play import ActionManager


class ArenaXGameBase(gym.Env):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "engine": "pygame",
    }

    def __init__(
        self,
        width: int,
        height: int,
        framerate: int,
        render_mode: str = "rgb_array",
        game_name: str = "SAI - Minigame",
        action_mapping: dict = {},
        seed: Optional[int] = None,
    ):
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.framerate = framerate
        self.game_name = game_name

        self.action_manager = ActionManager(action_mapping)

        self.time = 0
        self.frame = 1
        self.done = False
        self.truncated = False

        self.screen_width = width
        self.screen_height = height

        self.clock = pygame.time.Clock()
        self.set_render_mode(render_mode)

    ## Custom methods
    def set_render_mode(self, new_render_mode):
        self.close()
        self.render_mode = new_render_mode

        pygame.font.init()
        if self.render_mode == "human":
            pygame.display.init()
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )
            pygame.display.set_caption(self.game_name)
        else:
            self.screen = pygame.Surface((self.screen_width, self.screen_height))

    def get_human_action(self, keys_pressed):
        return self.action_manager.get_action(keys_pressed)

    ## Gym methods
    def reset(self, seed=None, options=None):
        """
        Reset the game to its initial state.
        """
        super().reset(seed=seed)

        self.time = 0
        self.frame = 1
        self.done = False
        self.truncated = False

    def step(self):
        """
        Move the game state forward one frame, given an action for the paddle(s).
        """
        # increment frame and update time
        self.frame += 1
        self.time = self.frame / self.framerate

    def render(self):
        """
        Render the game based on the mode.
        """
        if self.render_mode == "human":
            self.clock.tick(self.framerate)
            pygame.event.pump()
            pygame.display.flip()
        elif self.render_mode == "rgb_array":
            return np.copy(
                np.transpose(pygame.surfarray.pixels3d(self.screen), (1, 0, 2))
            )

    def close(self):
        pygame.quit()
