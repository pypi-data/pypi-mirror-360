import pygame
import numpy as np

from gymnasium.spaces import Discrete, Box

from sai_pygame.utils.env import ArenaXGameBase
from sai_pygame.utils.sprites import load_sprites_from_separate_files
from sai_pygame.utils.colors import BLACK

from .objects.drawable import Drawable
from .objects.basic_asset import BasicAsset

from .entities.player import Player, get_player_tile
from .entities.map import (
    Map,
    TILE_SIZE,
    grids,
    switch_assets,
    door_assets,
    get_channel_value,
    channel_reverse_mapping,
)

from .entities.map import X, SA, SE, G, DA, DE, P1, P2, channel_names
from .entities.gate import Gate, get_gate_from_switch, get_switch_from_gate

from .assets import GAME_ASSETS_BASE

# Game Constants
PLAYER_SIZE = 40
PLAYER_SPEED = 5
PLAYER_ONE_COLOR = (255, 255, 255)
PLAYER_TWO_COLOR = (211, 41, 207)
BACKGROUND_COLOR = (213, 213, 213)
GOAL_COLOR = (0, 255, 245)

valid_grids = {"small": 3, "med": 4, "large": 0}

FRAMERATE = 60
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900

ACTION_MAPPING = {
    "up": (pygame.K_w, 1),
    "down": (pygame.K_s, 2),
    "left": (pygame.K_a, 3),
    "right": (pygame.K_d, 4),
    "switch": (pygame.K_j, 9),
}


class CoopPuzzleEnv(ArenaXGameBase):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": FRAMERATE,
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
        "engine": "pygame",
        "reward_functions": [
            "classic",
        ],
    }

    def __init__(
        self,
        grid_size="large",
        render_mode="rgb_array",
        framerate=FRAMERATE,
        screen_width=SCREEN_WIDTH,  # Use this to resize screen
        screen_height=SCREEN_HEIGHT,  # Use this to resize screen
        seed=None,
        reward_function="classic",
        **kwargs,
    ):
        if grid_size not in valid_grids:
            raise ValueError("{} is not a valid grid size".format(grid_size))
        self.grid_index = valid_grids[grid_size]

        super().__init__(
            width=TILE_SIZE * len(grids[self.grid_index][0]),
            height=TILE_SIZE * len(grids[self.grid_index]),
            framerate=framerate,
            render_mode=render_mode,
            game_name="Co-op Puzzle - ArenaX Labs",
            action_mapping=ACTION_MAPPING,
            seed=seed,
            **kwargs,
        )

        # Terminal states
        self.TIME_LIMIT = 60 * 2  # 5 minutes

        # Sprite group
        self.all_sprites_list = pygame.sprite.Group()
        self.wall_colliders = []
        self.switch_colliders = []
        self.door_colliders = []
        self.goal_colliders = []
        self.shrub_shadows = {}
        self.switches = []
        self.gates = []
        self.active_switch = 0
        self.won_game = False
        self.player_on_goal = False
        self.player_moved = False
        self.player_switch = False
        self.player_collided_wall = False
        self.player_hit_switch = False
        self.player_hit_different_switch = False

        self.observation_channels = {key: [] for key in channel_names}

        # Environment Assets
        self.flower_sprites = self.get_colored_sprites("flower")
        self.shrub_sprites = self.get_colored_sprites("shrub", 3)
        self.env_sprites = self.get_environment_sprites()

        # Build Map
        self.screen.fill(BLACK)
        self.build_map(self.grid_index)

        # Players
        self.player_one = Player(
            self.get_player_sprites(1),
            "down",
            PLAYER_SIZE,
            self.player_one_start,
            self.screen_height,
            PLAYER_SPEED,
            self.wall_colliders,
            self.switch_colliders,
            self.door_colliders,
            self.floor.collider,
            self.goal_colliders,
            self,
        )
        self.player_two = Player(
            self.get_player_sprites(2),
            "up",
            PLAYER_SIZE,
            self.player_two_start,
            self.screen_height,
            PLAYER_SPEED,
            self.wall_colliders,
            self.switch_colliders,
            self.door_colliders,
            self.floor.collider,
            self.goal_colliders,
            self,
        )
        self.players = [self.player_one, self.player_two]
        self.active_player = 0
        self.end_turn_bool = False
        self.all_sprites_list.add(self.player_one, self.player_two)

        # reset game
        self.reset()

        # define action and observation space
        self.action_space = Discrete(10)
        self.observation_space = Box(
            low=-1,
            high=1,
            shape=(self.map.height, self.map.width, 13),
            dtype=np.float32,
        )

        # reward function
        self.reward_functions = {
            "classic": self._classic_reward,
        }
        self.reward_function = self.reward_functions[reward_function]
        assert self.reward_function is not None, "Invalid reward function"

        # get initial state
        self.init_obs = self.get_observation()

    def get_player_sprites(self, id):
        all_sprites = {
            "idle": pygame.image.load(
                "{}/player{}/stopped.png".format(GAME_ASSETS_BASE, id)
            )
        }
        for direction in ["down", "side", "up"]:
            all_sprites[direction] = load_sprites_from_separate_files(
                "{}/player{}/run-{}".format(GAME_ASSETS_BASE, id, direction), 2
            )
        return all_sprites

    def get_colored_sprites(self, name, num_variations=1):
        sprites = {}
        for color in ["blue", "orange", "pink", "white", "red"]:
            if num_variations == 1:
                asset_key = "{}/{}s/{}-{}.png".format(
                    GAME_ASSETS_BASE, name, name, color
                )
                sprites[color] = pygame.image.load(asset_key)
            else:
                for i in range(num_variations):
                    variation = "{}-{}--{}".format(name, color, i + 1)
                    asset_key = "{}/{}s/{}.png".format(
                        GAME_ASSETS_BASE, name, variation
                    )
                    sprites[variation] = pygame.image.load(asset_key)
        return sprites

    def get_environment_sprites(self):
        return {
            "grass--1": pygame.image.load(
                "{}/environment/grass--1.png".format(GAME_ASSETS_BASE)
            ),
            "grass--2": pygame.image.load(
                "{}/environment/grass--2.png".format(GAME_ASSETS_BASE)
            ),
            "grass--3": pygame.image.load(
                "{}/environment/grass--3.png".format(GAME_ASSETS_BASE)
            ),
            "grass--4": pygame.image.load(
                "{}/environment/grass--4.png".format(GAME_ASSETS_BASE)
            ),
            "grass--5": pygame.image.load(
                "{}/environment/grass--5.png".format(GAME_ASSETS_BASE)
            ),
            "grass-shadow": pygame.image.load(
                "{}/environment/grass-shadow.png".format(GAME_ASSETS_BASE)
            ),
            "wall": pygame.image.load(
                "{}/environment/wall.png".format(GAME_ASSETS_BASE)
            ),
            "cheese": pygame.image.load(
                "{}/environment/cheese.png".format(GAME_ASSETS_BASE)
            ),
        }

    def reset(self, **kwargs):
        """
        Reset the game to its initial state.
        """
        super().reset(**kwargs)
        self.active_switch = -1
        self.won_game = False
        self.active_player = 0
        self.end_turn_bool = False
        self.player_on_goal = False
        self.player_moved = False
        self.player_switch = False
        self.player_collided_wall = False
        self.player_hit_switch = False
        self.player_hit_different_switch = False

        for gate in self.gates:
            gate.set_gate_active(self.active_switch)

        self.player_one.update_position(self.player_one_start)
        self.player_two.update_position(self.player_two_start)
        self.player_one.reset()
        self.player_two.reset()

        observation = self.get_observation()
        info = {"timestep": self.frame}

        return observation, info

    def step(self, action):
        """
        Perform one step of the game, then extract the observation.
        """
        self.update(action)
        super().step()
        observation = self.get_observation()

        done = self.done
        truncated = done or self.TIME_LIMIT <= self.time  # Truncate at 2 min (at 60fps)
        reward = self.get_reward()

        info = {"timestep": self.frame}

        return observation, reward, done, truncated, info

    def update(self, action):
        """
        Move the game state forward one frame, given an action for the paddle(s).
        """

        # Update all sprites
        self.all_sprites_list.update()

        # Movement
        dir = self.get_direction(action)
        self.players[self.active_player].move(dir[1], dir[0])
        if action != 0 and action != 9:
            self.player_moved = True
            self.update_position_channel()

        if action == 9:
            if not self.end_turn_bool:
                self.end_turn()
                self.observation_channels["position"][
                    self.observation_channels["position"] != 0
                ] *= -1
                self.end_turn_bool = True
        else:
            self.end_turn_bool = False

        if self.won_game:
            self.won_game = False

        if self.TIME_LIMIT - self.time <= 0:
            self.done = True

    def render(self):
        """
        Render the game based on the mode.
        """
        # draw everything to the screen
        # self.screen.fill(BACKGROUND_COLOR)
        self.all_sprites_list.draw(self.screen)

        for player in self.players:
            player.update()

        return super().render()

    def get_observation(self):
        """
        Return the current observation from the game state.
        """
        return np.stack(
            [self.observation_channels[c] for c in channel_names], axis=2
        ).astype(np.float32)

    def get_reward(self):
        """
        Return the reward from the current game state.
        """
        return self.reward_function()

    def _classic_reward(self):
        reward = 0
        if self.done:
            reward = 1

        self.player_on_goal = False
        self.player_moved = False
        self.player_switch = False
        self.player_collided_wall = False
        self.player_hit_switch = False
        self.player_hit_different_switch = False

        return reward

    def end_turn(self):
        self.player_switch = True
        self.active_player += 1
        if self.active_player == len(self.players):
            self.active_player = 0

    def add_asset(self, AssetClass, sprite, x, y, random_rotation, group):
        tile = AssetClass(sprite, self.map.tile_size, random_rotation, group, self)
        tile.update_position(self.map.get_world_coordinates(x, y))
        self.all_sprites_list.add(tile)
        return tile

    def add_basic_asset(self, sprite, x, y, random_rotation=False, group=None):
        return self.add_asset(BasicAsset, sprite, x, y, random_rotation, group)

    def get_asset_key(self, group, num_variations):
        variation = self.np_random.integers(1, num_variations)
        return "{}--{}".format(group, variation)

    def add_array_to_channels(self):
        for channel_name in channel_names:
            self.observation_channels[channel_name].append([])

    def add_value_to_channels(self, output):
        for channel_name in channel_names:
            self.observation_channels[channel_name][-1].append(
                get_channel_value(channel_name, output, -1)
            )

    def format_channels(self):
        for channel_name in channel_names:
            self.observation_channels[channel_name] = np.flip(
                self.observation_channels[channel_name]
            )

    def update_door_switch_channel(self, channel_name, turned_on):
        value = -1
        if turned_on:
            value = 1
        self.observation_channels[channel_name] = (
            np.abs(self.observation_channels[channel_name]) * value
        )

    def update_position_channel(self):
        current_player_tiles = get_player_tile(self.players[self.active_player].rect)
        other_player_tiles = get_player_tile(
            self.players[(self.active_player + 1) % 2].rect
        )
        self.observation_channels["position"] = np.zeros(
            self.observation_channels["position"].shape
        )
        self.observation_channels["position"][current_player_tiles[0]][
            current_player_tiles[1]
        ] = 1
        self.observation_channels["position"][other_player_tiles[0]][
            other_player_tiles[1]
        ] = -1

    def build_map(self, map_index):
        self.map = Map(map_index)
        self.floor = Drawable(
            self.map.width * self.map.tile_size,
            self.map.height * self.map.tile_size,
            BACKGROUND_COLOR,
        )
        self.grass = []
        self.all_sprites_list.add(self.floor)
        for y in reversed(range(self.map.height)):
            self.add_array_to_channels()
            for x in reversed(range(self.map.width)):
                self.add_basic_asset(
                    self.env_sprites[self.get_asset_key("grass", 5)], x, y, True
                )

                output = self.map.grid[y][x]
                self.add_value_to_channels(output)
                if output >= SA and output <= SE:
                    switch = self.add_basic_asset(
                        self.flower_sprites[switch_assets[output]], x, y, False, output
                    )
                    self.switch_colliders.append(switch.collider)
                    self.switches.append(switch)
                elif output >= DA and output <= DE:
                    shrub_shadow = self.add_basic_asset(
                        self.env_sprites["grass-shadow"], x, y + 0.2, False
                    )
                    if output not in self.shrub_shadows:
                        self.shrub_shadows[output] = []
                    self.shrub_shadows[output].append(shrub_shadow)
                    gate = self.add_asset(
                        Gate,
                        self.shrub_sprites[
                            self.get_asset_key(
                                "shrub-{}".format(door_assets[output]), 3
                            )
                        ],
                        x,
                        y,
                        True,
                        output,
                    )
                    self.door_colliders.append(gate.collider)
                    self.gates.append(gate)
                elif output == X:
                    if self.map.grid[y + 1][x] != X:
                        self.add_basic_asset(
                            self.env_sprites["grass-shadow"], x, y + 0.2, False
                        )
                    wall = self.add_basic_asset(self.env_sprites["wall"], x, y, True)
                    self.wall_colliders.append(wall.collider)
                elif output == P1:
                    self.player_one_start = self.map.get_world_coordinates(x, y)
                elif output == P2:
                    self.player_two_start = self.map.get_world_coordinates(x, y)
                elif output == G:
                    goal = self.add_basic_asset(self.env_sprites["cheese"], x, y, False)
                    self.goal_colliders.append(goal.collider)
        self.format_channels()

    def update_switch(self, switch_group):
        self.player_hit_switch = True
        target_gate = get_gate_from_switch(switch_group)
        if switch_group == self.active_switch:
            return

        gates_updated = {}
        for gate in self.gates:
            gate.set_gate_active(switch_group)
            gate_name = channel_reverse_mapping[gate.group]
            if gate_name not in gates_updated:
                current_switch = get_switch_from_gate(gate.group)
                self.update_door_switch_channel(
                    channel_reverse_mapping[current_switch],
                    current_switch == switch_group,
                )
                self.update_door_switch_channel(
                    channel_reverse_mapping[gate.group], gate.group == target_gate
                )
                gates_updated[gate_name] = True

        for group, shadows in self.shrub_shadows.items():
            if group == get_gate_from_switch(switch_group):
                alpha = 0
            else:
                alpha = 255
            for shadow in shadows:
                shadow.image.set_alpha(alpha)

        self.player_hit_different_switch = True
        self.active_switch = switch_group

    def player_reached_goal(self):
        self.player_on_goal = True
        if self.player_one.on_goal and self.player_two.on_goal:
            self.won_game = True
            self.done = True

    def player_collided(self, gate):
        if not gate:
            self.player_collided_wall = True

    def get_direction(self, action):
        if action == 1:
            return [-1, -1]
        elif action == 2:
            return [-1, 1]
        elif action == 3:
            return [-1, 0]
        elif action == 4:
            return [1, -1]
        elif action == 5:
            return [1, 1]
        elif action == 6:
            return [1, 0]
        elif action == 7:
            return [0, -1]
        elif action == 8:
            return [0, 1]
        else:
            return [0, 0]
