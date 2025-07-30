import pygame
import gymnasium as gym

class BasicAsset(pygame.sprite.Sprite):
    def __init__(self, sprite, size, random_rotation, group, env: gym.Env):
        super().__init__()
        self.image = pygame.transform.scale(sprite, (size, size))
        if random_rotation:
            rotation = env.np_random.integers(1, 4) * 90
            self.image = pygame.transform.rotate(self.image, rotation)
        self.rect = self.image.get_rect()
        self.collider = self.rect.copy()
        self.group = group

    def update_position(self, coordinates):
        self.rect.x = coordinates[0]
        self.rect.y = coordinates[1]
        self.collider.x = coordinates[0]
        self.collider.y = coordinates[1]
