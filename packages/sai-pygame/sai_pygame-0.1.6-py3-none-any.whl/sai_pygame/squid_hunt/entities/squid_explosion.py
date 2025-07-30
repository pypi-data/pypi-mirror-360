from sai_pygame.utils.animation import AnimationBase


class SquidExplosion(AnimationBase):
    def __init__(self, explosion_sprites, position, size, game):
        super().__init__(explosion_sprites, position, size, 3, [5, 5, 5])
        self.game = game

    def update(self):
        kill_bool = super().update(loop_bool=True)

        if kill_bool:
            self.game.all_sprites_list.remove(self)

        return kill_bool
