import pygame
import os

fonts = {"thick": "retro-pixel-thick.ttf", "arcade": "retro-pixel-arcade.ttf"}


def load_font(font_name, size):
    font_path = os.path.join(os.path.dirname(__file__), font_name)
    return pygame.font.Font(font_path, size)
