from gymnasium import register

__version__ = "0.1.0"

register(
    id="CoopPuzzle-v0",
    entry_point="sai_pygame.coop_puzzle:CoopPuzzleEnv",
)

register(
    id="Pong-v0",
    entry_point="sai_pygame.pong:PongEnv",
)

register(
    id="SpaceEvaders-v0",
    entry_point="sai_pygame.space_evaders:SpaceEvadersEnv",
)

register(
    id="SquidHunt-v0",
    entry_point="sai_pygame.squid_hunt:SquidHuntEnv",
)

## Import Future Environments if Available
try:
    import sai_pygame._future
except:
    pass
