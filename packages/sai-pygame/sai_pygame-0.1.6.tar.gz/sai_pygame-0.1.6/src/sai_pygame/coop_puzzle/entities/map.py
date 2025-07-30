X = 1  # wall
SA = 2  # switch RED
SB = 3  # switch GREEN
SC = 4  # switch ORANGE
SD = 5  # switch YELLOW
SE = 6  # switch BLUE
G = 7  # goal
DA = 8  # door
DB = 9  # door
DC = 10  # door
DD = 11  # door
DE = 12  # door
P1 = 13  # player 1 start
P2 = 14  # player 2 start

TILE_SIZE = 32

channel_names = [
    "position",
    "walls",
    "switch--A",
    "switch--B",
    "switch--C",
    "switch--D",
    "switch--E",
    "door--A",
    "door--B",
    "door--C",
    "door--D",
    "door--E",
    "goal",
]

channel_mapping = {
    "position": P1,
    "walls": X,
    "switch--A": SA,
    "switch--B": SB,
    "switch--C": SC,
    "switch--D": SD,
    "switch--E": SE,
    "door--A": DA,
    "door--B": DB,
    "door--C": DC,
    "door--D": DD,
    "door--E": DE,
    "goal": G,
}
channel_reverse_mapping = {value: key for key, value in channel_mapping.items()}


def get_channel_value(channel_name, output, open_multiple=1):
    if channel_name == "position":
        if output == P1:
            return 1  # Need to make this dynamic based on who is controlling
        elif output == P2:
            return -1  # Need to make this dynamic based on who is controlling
        else:
            return 0
    else:
        value = int(channel_mapping[channel_name] == output)
        if channel_name != "goal":
            value *= open_multiple
        return value


switch_assets = {SA: "blue", SB: "orange", SC: "pink", SD: "white", SE: "red"}

door_assets = {DA: "blue", DB: "orange", DC: "pink", DD: "white", DE: "red"}

GRID_A = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, SA, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, P1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, SB, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [X, X, X, X, X, X, X, X, X, X, X, DD, DD, DD, X, X, X, X, X, X, X, X, X, X, X],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, SD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, SA, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [X, X, X, X, X, X, X, X, X, X, X, DB, DB, DB, X, X, X, X, X, X, X, X, X, X, X],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, SC, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, SC, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [X, X, X, X, X, X, X, X, X, X, X, DE, DE, DE, X, X, X, X, X, X, X, X, X, X, X],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, SB, 0, 0, 0, 0, 0, 0, 0, G, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, SD, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [
        X,
        X,
        X,
        X,
        DC,
        DC,
        DC,
        X,
        X,
        X,
        X,
        X,
        X,
        X,
        DA,
        DA,
        DA,
        X,
        X,
        DB,
        DB,
        DB,
        X,
        X,
        X,
    ],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, X, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, SE, 0, 0, 0, 0, 0, 0, 0, 0, X, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, SD, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, X, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [X, X, X, X, DD, DD, DD, X, X, X, X, X, X, X, DC, DC, DC, X, X, X, X, X, X, X, X],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, SC, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, SA, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [X, X, X, X, X, X, X, X, X, X, X, DA, DA, DA, X, X, X, X, X, X, X, X, X, X, X],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, P2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, SB, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

GRID_B = [
    [0, 0, 0, 0, 0],
    [0, 0, P1, 0, 0],
    [0, 0, 0, 0, 0],
    [0, G, G, G, 0],
    [0, G, G, G, 0],
    [0, 0, 0, 0, 0],
    [0, 0, P2, 0, 0],
    [0, 0, 0, 0, 0],
]

GRID_C = [
    [0, 0, 0, 0, 0],
    [0, 0, P1, 0, 0],
    [0, 0, 0, 0, 0],
    [X, X, X, 0, 0],
    [0, G, G, G, 0],
    [0, G, G, G, 0],
    [0, 0, 0, 0, 0],
    [0, 0, P2, 0, 0],
    [0, 0, 0, 0, 0],
]

GRID_D = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, SA, 0, P1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [X, X, DA, DA, DA, X, X],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, G, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, P2, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
]

GRID_E = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, SC, 0, 0, 0, 0, P1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [X, X, X, X, X, DA, DA, DA, X, X, X, X, X],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, SB, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [X, X, DB, DB, DB, X, X, X, X, X, X, X, X],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, G, 0, 0, 0, 0, SA, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [X, X, X, X, X, X, X, X, DB, DB, DB, X, X],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, SB, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [X, X, X, DC, DC, DC, X, X, X, X, X, X, X],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, P2, 0, 0, 0, 0, SB, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

grids = [GRID_A, GRID_B, GRID_C, GRID_D, GRID_E]


class Map:
    def __init__(self, grid_index):
        self.grid = grids[grid_index]
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.tile_size = 32

    def get_world_coordinates(self, x, y):
        return [x * self.tile_size, y * self.tile_size]
