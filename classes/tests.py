import unittest

from room import Room
from player import Player
from item import Item


class TestGame(unittest.TestCase):

    def test_room_connection(self):

        room1 = Room("Room1", "")
        room2 = Room("Room2", "")

        room1.connect("north", room2)

        player = Player(room1)

        player.move("north")

        self.assertEqual(
            player.current_room,
            room2
        )

    def test_take_item(self):

        room = Room("Room", "")

        key = Item("Key", "Rusty key")

        room.add_item(key)

        player = Player(room)

        player.take("Key")

        self.assertTrue(
            player.has_item("Key")
        )

    def test_inventory(self):

        room = Room("Room", "")

        key = Item("Key", "Rusty key")

        room.add_item(key)

        player = Player(room)

        player.take("Key")

        self.assertIn(
            "Key",
            player.show_inventory()
        )


if __name__ == "__main__":
    unittest.main()