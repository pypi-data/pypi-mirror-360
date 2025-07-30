import pygame

from .input_tracker import InputTracker


class ActionManager:
    def __init__(self, action_bindings: dict):
        """
        Initialize with a dictionary of action bindings.
        action_bindings: dict where each key is an action name and value is a tuple of (pygame_key, action_value)
        Example: {
            "move_up": (pygame.K_w, 1),
            "shoot": (pygame.K_SPACE, 9),
            ...
        }
        """
        self.action_bindings = action_bindings
        self.input_tracker = InputTracker(
            [key for key, _ in self.action_bindings.values()]
        )

    def print_input_mapping(self):
        print("\nInput Mappings\n")
        for action, (key, _) in self.action_bindings.items():
            print("{}: {}".format(action, pygame.key.name(key).upper()))

    def get_action(self, keys_pressed):
        """
        Returns action based on keys pressed using the configured bindings.
        Supports both additive and override actions based on the binding configuration.
        """
        self.input_tracker.press(keys_pressed)
        action = 0

        # Process regular key presses
        for action_name, (key, value) in self.action_bindings.items():
            if keys_pressed[key]:
                if isinstance(value, (int, float)):
                    # Additive action
                    action += value
                elif callable(value):
                    # Custom action function
                    action = value(action)
                else:
                    # Override action
                    action = value

        return action
