import pygame


class AnimationBase(pygame.sprite.Sprite):
    def __init__(self, sprites, position, size, num_frames, frame_frequencies=[]):
        super().__init__()
        self.sprites = sprites
        self.position = position
        self.num_frames = num_frames
        self.base_size = size
        if isinstance(size, int):
            self.sizes = (size, size)
        elif isinstance(size, tuple) and len(size) == 2:
            self.sizes = size
        else:
            raise ValueError("Size must be an int or a tuple of two ints.")
        self.frame = 0
        self.time_on_frame = 0
        self.invert_axis = {"x": False, "y": False}
        self.rotation = None
        self.change_sprite()
        self.empty_surface = pygame.Surface([0, 0])
        self.rect = self.image.get_rect(center=(position[0], position[1]))
        if len(frame_frequencies) == 0:
            self.frame_frequencies = [3 for _ in range(num_frames)]
        else:
            self.frame_frequencies = frame_frequencies

    def update_frame(self):
        self.time_on_frame += 1
        if self.frame >= self.num_frames:
            return True
        if self.time_on_frame >= self.frame_frequencies[self.frame]:
            self.frame += 1
            self.time_on_frame = 0
        return self.frame == self.num_frames

    def change_sprite(self):
        image = self.sprites[self.frame]
        image = pygame.transform.scale(image, (self.sizes[0], self.sizes[1]))
        image = pygame.transform.flip(
            image, self.invert_axis["x"], self.invert_axis["y"]
        )
        if self.rotation is not None:
            image = pygame.transform.rotate(image, self.rotation)
        self.base_image = image
        self.image = image

    def reset_animation(self):
        self.frame = 0
        self.time_on_frame = 0

    def update(self, loop_bool=False, stay_on_last_frame=False):
        kill_bool = self.update_frame()
        if not kill_bool:
            self.change_sprite()
        elif not stay_on_last_frame:
            if loop_bool:
                self.reset_animation()
            else:
                self.image = self.empty_surface
        return kill_bool
