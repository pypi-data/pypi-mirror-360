from sai_pygame.utils.colors import WHITE
from sai_pygame.utils.fonts import load_font, fonts


class Text:
    def __init__(self, x, y, string, size, game):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.game = game
        self.screen_width = game.screen_width
        self.screen_height = game.screen_height
        self.update(string)

    def update(self, string):
        self.image = load_font(fonts["thick"], self.size).render(string, 1, WHITE)
