class Flags:
    def __init__(self):
        self.flags = {}

    def set(self, key, value=True):
        self.flags[key] = value

    def get(self, key):
        return self.flags.get(key, False)