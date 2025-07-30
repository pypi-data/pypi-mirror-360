import pygame
import os


def get_tile(sheet, tile_width, tile_height, tile_row, tile_column):
    x = tile_column * tile_width
    y = tile_row * tile_height
    return sheet.subsurface((x, y, tile_width, tile_height))


def load_spritesheet(filename, num_tiles, mapping):
    image_path = os.path.join(os.path.dirname(__file__), filename)
    sheet = pygame.image.load(image_path)
    sheet = pygame.transform.scale(sheet, (num_tiles[0] * 40, num_tiles[1] * 40))
    sheet_width, sheet_height = sheet.get_size()
    tile_width = sheet_width // num_tiles[0]
    tile_height = sheet_height // num_tiles[1]
    sprite_sheet = {}
    for data in mapping:
        sprite_sheet[data[2]] = get_tile(
            sheet, tile_width, tile_height, data[1], data[0]
        )
    return sprite_sheet


def load_sprites_from_separate_files(file_prepend, num_sprites):
    sprite_sheet = {}
    for i in range(num_sprites):
        image_path = os.path.join(
            os.path.dirname(__file__), "{}-{}.png".format(file_prepend, i + 1)
        )
        sprite_sheet[i] = pygame.image.load(image_path)
    return sprite_sheet
