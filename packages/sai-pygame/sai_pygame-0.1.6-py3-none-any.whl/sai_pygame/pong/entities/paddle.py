import pygame

BLACK = (0, 0, 0)


class Paddle(pygame.sprite.Sprite):
    def __init__(self, color, width, height, screen_height, speed):
        super().__init__()

        self.screen_height = screen_height
        self.width = width
        self.height = height
        self.speed = speed

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        pygame.draw.rect(self.image, color, [0, 0, self.width, self.height])

        self.rect = self.image.get_rect()

    def moveUp(self):
        if self.rect.y > 0:  # Can move until top edge
            self.rect.y = max(0, self.rect.y - self.speed)


    def moveDown(self):
        if self.rect.y + self.height < self.screen_height:  # Can move until bottom edge
            self.rect.y = min(self.screen_height - self.height, self.rect.y + self.speed)
