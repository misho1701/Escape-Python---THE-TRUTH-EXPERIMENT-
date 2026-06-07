class Player:
    def __init__(self, starting_room):
        self.current_room = starting_room
        self.inventory = []

    def move(self, direction):

        if direction in self.current_room.connections:
            self.current_room = self.current_room.connections[direction]
            return f"You move to {self.current_room.name}."

        return "You can't go that way."

    def take(self, item_name):

        for item in self.current_room.items:

            if item.name.lower() == item_name.lower():

                self.inventory.append(item)
                self.current_room.remove_item(item)

                return f"You picked up {item.name}."

        return "Item not found."

    def has_item(self, item_name):

        return any(
            item.name.lower() == item_name.lower()
            for item in self.inventory
        )

    def show_inventory(self):

        if not self.inventory:
            return "Inventory is empty."

        return "\n".join(
            f"- {item.name}"
            for item in self.inventory
        )