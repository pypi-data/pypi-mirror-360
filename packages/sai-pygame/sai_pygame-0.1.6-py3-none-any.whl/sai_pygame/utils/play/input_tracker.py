class InputTracker:
    def __init__(self, keys_to_track):
        self.keys_to_track = keys_to_track
        self.pressed = {}
        self.held = {}
        self.reset()

    def press(self, keys_pressed):
        for key in self.keys_to_track:
            self.pressed[key] = keys_pressed[key]
            if keys_pressed[key]:
                self.held[key] += 1
            else:
                self.held[key] = 0

    def reset(self):
        for key in self.keys_to_track:
            self.pressed[key] = False
            self.held[key] = 0
