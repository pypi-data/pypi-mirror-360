from ..objects.basic_asset import BasicAsset

SPACE_BETWEEN_SWITCH_AND_GATE = 6


def get_gate_from_switch(switch_group):
    return switch_group + SPACE_BETWEEN_SWITCH_AND_GATE


def get_switch_from_gate(switch_group):
    return switch_group - SPACE_BETWEEN_SWITCH_AND_GATE


class Gate(BasicAsset):
    def __init__(self, sprite, size, random_rotation, group, env):
        super().__init__(sprite, size, random_rotation, group, env)
        self.use_collider = True

    def set_gate_active(self, switch_group):
        active = self.group != get_gate_from_switch(switch_group)
        self.use_collider = active
        alpha = 255 if active else 50
        self.image.set_alpha(alpha)
