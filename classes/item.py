class Item:

    def __init__(self, name, description, item_type="misc", usable=False, power=None, hint=None):

        self.name = name
        self.description = description
        self.type = item_type
        self.usable = usable
        self.power = power
        self.hint = hint

    def inspect(self):

        info = f"{self.name}: {self.description}"

        if self.hint:
            info += f"\nHint: {self.hint}"

        return info

    def __str__(self):
        return self.name