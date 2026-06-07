class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description

        self.connections = {}
        self.items = []
        self.puzzle = None

    def connect(self, direction, room):
        self.connections[direction] = room

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def list_items(self):
        if not self.items:
            return "No visible items."

        return "\n".join(
            f"- {item.name}: {item.description}"
            for item in self.items
        )