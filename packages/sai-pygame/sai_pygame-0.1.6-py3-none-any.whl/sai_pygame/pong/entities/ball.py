import pygame
import gymnasium as gym
from .paddle import Paddle
BLACK = (0, 0, 0)


class Ball(pygame.sprite.Sprite):
    def __init__(self, env: gym.Env, color, diameter, screen_width, screen_height, max_speed=7):
        super().__init__()

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.diameter = diameter
        self.env = env

        self.max_speed = max_speed

        self.image = pygame.Surface([self.diameter, self.diameter])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        pygame.draw.rect(self.image, color, [0, 0, self.diameter, self.diameter])

        self.rect = self.image.get_rect()
        self.velocity: list[float] = [0.0, 0.0]
        self.reset()

    def reset(self):
        direction = self.env.np_random.choice([-1, 1])
        self.velocity: list[float] = [
            direction * self.env.np_random.integers(3, self.max_speed),
            self.env.np_random.integers(-3, 3),
        ]
        # Center the ball
        self.rect.x = self.screen_width // 2 - self.diameter // 2
        self.rect.y = self.screen_height // 2 - self.diameter // 2

    def update(self):
        self.rect.x += int(self.velocity[0])
        self.rect.y += int(self.velocity[1])

    def bounce(self, paddle: Paddle):
        self.velocity[0] = max(-self.max_speed, min(self.max_speed, self.velocity[0] * -1.1) )
    
        # Calculate where ball hit the paddle (0.0 = top, 1.0 = bottom)
        ball_center_y = self.rect.centery
        paddle_center_y = paddle.rect.centery
        paddle_half_height = paddle.height / 2
        
        # Hit position: -1.0 (top) to 1.0 (bottom)
        hit_position = (ball_center_y - paddle_center_y) / paddle_half_height
        hit_position = max(-1.0, min(1.0, hit_position))

        # Add random valruable to prevent constant left-right movement
        if abs(hit_position) < 0.1:
            hit_position += self.env.np_random.uniform(-0.1, 0.1)
        
        # Set vertical velocity based on hit position
        self.velocity[1] = hit_position * self.max_speed
