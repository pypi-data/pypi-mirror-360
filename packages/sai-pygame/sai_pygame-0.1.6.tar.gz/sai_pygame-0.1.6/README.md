# ArenaX Lab's PyGame Environments

This package contains the PyGame environments used for the SAI Platform.

## Installation

```bash
pip install sai-pygame
```

## Usage

```python
import gymnasium as gym
import sai_pygame

env = gym.make("CoopPuzzle-v0", render_mode="human")
```


# Environment List

- `CoopPuzzle-v0`: A cooperative puzzle game where two players work together to solve a puzzle.
- `Pong-v0`: A game where two players compete to hit a ball back and forth.
- `SpaceEvaders-v0`: A game where a player must avoid incoming asteroids.
- `SquidHunt-v0`: A game where a player must hunt down squids while avoiding obstacles.


# More Information

- [SAI Platform](https://competesai.com)
- [SAI Documentation](https://docs.competesai.com)
