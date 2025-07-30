import pygame
import numpy as np

from gymnasium.spaces import Discrete, Box

from sai_pygame.utils.env import ArenaXGameBase
from sai_pygame.utils.colors import WHITE, BLACK

from .entities.paddle import Paddle
from .entities.ball import Ball

# Game Constants
PADDLE_START_X = 20
PADDLE_START_Y = 200
PADDLE_SPEED = 5
MAX_VELOCITY = 7

# Config
SCREEN_WIDTH = 704
SCREEN_HEIGHT = 480
FRAMERATE = 60

# Action Mapping
ACTION_MAPPING = {
    "up": (pygame.K_w, 1),
    "down": (pygame.K_s, 2),
}


class PongEnv(ArenaXGameBase):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": FRAMERATE,
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
        "engine": "pygame",
        "reward_functions": ["classic"],
    }

    def __init__(
        self,
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        framerate=FRAMERATE,
        render_mode="rgb_array",
        reward_function="classic",
        max_velocity=MAX_VELOCITY,
        seed=None,
        **kwargs,
    ):
        super().__init__(
            width,
            height,
            framerate=framerate,
            render_mode=render_mode,
            game_name="Pong - ArenaX Labs",
            action_mapping=ACTION_MAPPING,
            seed=seed,
            **kwargs,
        )
        # initialize custom variables
        self.TIME_LIMIT = 120
        self.ball_size = self.screen_width / 70
        self.paddle_width = self.screen_width / 70
        self.paddle_height = self.screen_height / 5

        self.max_velocity = max_velocity

        # Level based progression
        self.level = 1
        self.base_opponent_speed = 1
        self.current_opponent_speed = self.base_opponent_speed
        self.speed_increase_per_level = 1

        self.winner = ""

        # initialize paddles and ball
        self.paddleA = Paddle(
            WHITE,
            self.paddle_width,
            self.paddle_height,
            self.screen_height,
            PADDLE_SPEED,
        )
        self.paddleB = Paddle(
            WHITE,
            self.paddle_width,
            self.paddle_height,
            self.screen_height,
            self.current_opponent_speed,
        )
        self.ball = Ball(
            self,
            WHITE,
            self.ball_size,
            self.screen_width,
            self.screen_height,
            self.max_velocity,
        )

        # create a group of sprites for easier updating and rendering
        self.all_sprites_list = pygame.sprite.Group()
        self.all_sprites_list.add(self.paddleA, self.paddleB, self.ball)

        # reset game
        self.reset()

        # Define action and observation space
        self.action_space = Discrete(3)
        self.observation_space = Box(
            low=np.array(
                [-1, -1, -1, -1, -1, -1]
            ),  # Normalized values between -1 and 1
            high=np.array([1, 1, 1, 1, 1, 1]),
            dtype=np.float32,
        )

        # initialize reward function
        self.reward_functions = {
            "classic": self._classic_reward,
        }
        self.reward_function = self.reward_functions[reward_function]
        assert self.reward_function is not None, (
            f"Reward function {reward_function} not found"
        )

        # initialize observation
        self.init_obs = self.get_observation()

    def reset(self, **kwargs):
        """
        Reset the game to its initial state.
        """
        super().reset(**kwargs)

        # reset the game environment back to the initial state
        self.level = 1
        self.current_opponent_speed = self.base_opponent_speed
        self.paddleB.speed = self.current_opponent_speed
        self.winner = ""

        # Position paddles and ball to their start positions
        self._reset_positions()

        observation = self.get_observation()

        info = {
            "timestep": self.frame,
            "screen_height": self.screen_height,
            "screen_width": self.screen_width,
            "paddle_height": self.paddle_height,
            "ball_position": self.ball.rect.center,
            "left_paddle_position": self.paddleA.rect.center,
            "right_paddle_position": self.paddleB.rect.center,
        }

        return observation, info

    def move_opponent(self):
        """
        Move the opponent paddle towards the ball.
        """

        if self.np_random.random() < 0.10:  # 10% chance to make mistake
            return

        ball_center_y = self.ball.rect.y + self.ball.diameter / 2

        aim_position = self.np_random.random()  # Random float between 0.0 and 1.0
        aim_position = max(0.1, min(0.9, aim_position))

        # Calculate the target Y position on the paddle
        target_paddle_y = self.paddleB.rect.y + (aim_position * self.paddleB.height)

        if ball_center_y < target_paddle_y:
            self.paddleB.moveUp()
        else:
            self.paddleB.moveDown()

    def check_collisions(self):
        """
        Check for collisions with walls and paddles, adjust game state accordingly.
        """
        # Wall collision
        if self.ball.rect.x >= self.screen_width - self.ball.diameter:
            self.winner = "A"
        elif self.ball.rect.x <= 0:
            self.done = True
            self.winner = "B"

        if (
            self.ball.rect.y >= self.screen_height - self.ball.diameter
            or self.ball.rect.y <= 0
        ):
            self.ball.velocity[1] = -self.ball.velocity[1]

        # Paddle collision
        if pygame.sprite.collide_mask(self.ball, self.paddleA):
            self.ball.bounce(self.paddleA)

        if pygame.sprite.collide_mask(self.ball, self.paddleB):
            self.ball.bounce(self.paddleB)

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
        if self.winner == "A":
            self.increase_difficulty()

        info = {
            "timestep": self.frame,
            "screen_height": self.screen_height,
            "screen_width": self.screen_width,
            "paddle_height": self.paddle_height,
            "ball_position": self.ball.rect.center,
            "left_paddle_position": self.paddleA.rect.center,
            "right_paddle_position": self.paddleB.rect.center,
        }

        return observation, reward, done, truncated, info

    def update(self, action):
        """
        Move the game state forward one frame, given an action for the paddle(s).
        """
        # game loop goes here

        # Update all sprites
        self.all_sprites_list.update()

        # Move paddles according to the action
        if action == 1:
            self.paddleA.moveUp()
        elif action == 2:
            self.paddleA.moveDown()

        # Ball and wall collision logic
        self.check_collisions()
        if self.TIME_LIMIT - self.time <= 0:
            self.truncated = True

        # Move opponent paddle
        self.move_opponent()

    def render(self):
        """
        Render the game based on the mode.
        """
        # draw everything to the screen
        self.screen.fill(BLACK)
        self.all_sprites_list.draw(self.screen)
        return super().render()

    def get_paddle_position(self, y):
        """Convert paddle y position to normalized coordinates between -1 and 1"""
        # Remove the scaling factor and simply normalize to [-1, 1]
        return (y / self.screen_height - 0.5) * 2

    def _reset_positions(self):
        """
        Reset the positions of the paddles and ball to their initial state.
        """
        self.winner = ""
        self.paddleA.rect.y = PADDLE_START_Y
        self.paddleB.rect.y = PADDLE_START_Y
        self.paddleB.rect.x = self.screen_width - PADDLE_START_X - self.paddle_width
        self.paddleA.rect.x = PADDLE_START_X

        self.ball.reset()

    def increase_difficulty(self):
        """
        Increase the difficulty of the game
        """
        self.current_opponent_speed += self.speed_increase_per_level
        self.paddleB.speed = self.current_opponent_speed
        self._reset_positions()

    def get_observation(self):
        """
        Return the current observation from the game state.
        """
        return np.array(
            [
                self.get_paddle_position(self.paddleA.rect.y),
                self.get_paddle_position(self.paddleB.rect.y),
                (self.ball.rect.center[0] / self.screen_width - 0.5) * 2,
                (self.ball.rect.center[1] / self.screen_height - 0.5) * 2,
                self.ball.velocity[0] / self.screen_width,
                self.ball.velocity[1] / self.screen_height,
            ],
            dtype=np.float32,
        )

    def get_reward(self):
        """
        Return the reward from the current game state.
        """
        return self.reward_function()

    def _classic_reward(self):
        # Reward the agent if they are the winner
        if self.winner == "A":
            return 1 * self.level
        elif self.winner == "B":
            return -1
        return 0
