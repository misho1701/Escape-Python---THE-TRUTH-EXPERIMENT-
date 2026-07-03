import unittest
import json
import os
import tempfile

from room import Room
from player import Player
from item import Item
from puzzle import Puzzle
from npc import NPC
from achievements import Achievements
from endings import Endings
from save_manager import SaveManager
from game import Game
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from gui import EscapePygameGUI


class TestRoom(unittest.TestCase):

    def setUp(self):
        self.room = Room("TestRoom", "A test room.")

    def test_room_name(self):
        self.assertEqual(self.room.name, "TestRoom")

    def test_room_description(self):
        self.assertEqual(self.room.description, "A test room.")

    def test_room_starts_empty(self):
        self.assertEqual(self.room.items, [])
        self.assertIsNone(self.room.puzzle)
        self.assertEqual(self.room.connections, {})

    def test_connect_rooms(self):
        other = Room("Other", "Another room.")
        self.room.connect("north", other)
        self.assertIn("north", self.room.connections)
        self.assertEqual(self.room.connections["north"], other)

    def test_add_item(self):
        item = Item("Key", "A key.")
        self.room.add_item(item)
        self.assertIn(item, self.room.items)

    def test_remove_item(self):
        item = Item("Key", "A key.")
        self.room.add_item(item)
        self.room.remove_item(item)
        self.assertNotIn(item, self.room.items)

    def test_remove_item_not_present(self):
        item = Item("Key", "A key.")
        self.room.remove_item(item)

    def test_list_items_empty(self):
        self.assertEqual(self.room.list_items(), "No visible items.")

    def test_list_items_with_items(self):
        item = Item("Key", "A rusty key.")
        self.room.add_item(item)
        result = self.room.list_items()
        self.assertIn("Key", result)
        self.assertIn("A rusty key.", result)

    def test_multiple_connections(self):
        north = Room("North", "")
        south = Room("South", "")
        self.room.connect("north", north)
        self.room.connect("south", south)
        self.assertEqual(len(self.room.connections), 2)


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.room = Room("Start", "Starting room.")
        self.player = Player(self.room)

    def test_starting_room(self):
        self.assertEqual(self.player.current_room, self.room)

    def test_inventory_starts_empty(self):
        self.assertEqual(self.player.inventory, [])

    def test_move_valid_direction(self):
        other = Room("Other", "")
        self.room.connect("east", other)
        result = self.player.move("east")
        self.assertEqual(self.player.current_room, other)
        self.assertIn("Other", result)

    def test_move_invalid_direction(self):
        result = self.player.move("north")
        self.assertIn("can't", result.lower())
        self.assertEqual(self.player.current_room, self.room)

    def test_take_item(self):
        item = Item("Key", "A key.")
        self.room.add_item(item)
        result = self.player.take("Key")
        self.assertIn(item, self.player.inventory)
        self.assertNotIn(item, self.room.items)
        self.assertIn("Key", result)

    def test_take_item_case_insensitive(self):
        item = Item("Key", "A key.")
        self.room.add_item(item)
        self.player.take("key")
        self.assertIn(item, self.player.inventory)

    def test_take_item_not_found(self):
        result = self.player.take("Sword")
        self.assertIn("not found", result.lower())

    def test_has_item_true(self):
        item = Item("Key", "A key.")
        self.player.inventory.append(item)
        self.assertTrue(self.player.has_item("Key"))

    def test_has_item_false(self):
        self.assertFalse(self.player.has_item("Key"))

    def test_has_item_case_insensitive(self):
        item = Item("Key", "A key.")
        self.player.inventory.append(item)
        self.assertTrue(self.player.has_item("key"))
        self.assertTrue(self.player.has_item("KEY"))

    def test_show_inventory_empty(self):
        result = self.player.show_inventory()
        self.assertIn("empty", result.lower())

    def test_show_inventory_with_items(self):
        item = Item("Key", "A key.")
        self.player.inventory.append(item)
        result = self.player.show_inventory()
        self.assertIn("Key", result)

    def test_show_inventory_multiple_items(self):
        for name in ["Key", "Note", "Wire"]:
            self.player.inventory.append(Item(name, ""))
        result = self.player.show_inventory()
        for name in ["Key", "Note", "Wire"]:
            self.assertIn(name, result)


class TestItem(unittest.TestCase):

    def test_basic_item(self):
        item = Item("Key", "A rusty key.")
        self.assertEqual(item.name, "Key")
        self.assertEqual(item.description, "A rusty key.")
        self.assertEqual(item.type, "misc")
        self.assertFalse(item.usable)
        self.assertIsNone(item.power)
        self.assertIsNone(item.hint)

    def test_item_with_all_fields(self):
        item = Item("Battery", "A battery.", item_type="tool",
                    usable=True, power=10, hint="Needs wire.")
        self.assertEqual(item.type, "tool")
        self.assertTrue(item.usable)
        self.assertEqual(item.power, 10)
        self.assertEqual(item.hint, "Needs wire.")

    def test_inspect_no_hint(self):
        item = Item("Key", "A rusty key.")
        result = item.inspect()
        self.assertIn("Key", result)
        self.assertIn("A rusty key.", result)

    def test_inspect_with_hint(self):
        item = Item("Key", "A rusty key.", hint="Try it on the door.")
        result = item.inspect()
        self.assertIn("Try it on the door.", result)

    def test_str(self):
        item = Item("Key", "A key.")
        self.assertEqual(str(item), "Key")


class TestPuzzle(unittest.TestCase):

    def setUp(self):
        self.puzzle = Puzzle("What is 2+2?", "4", "Correct!")

    def test_initial_state(self):
        self.assertFalse(self.puzzle.solved)
        self.assertEqual(self.puzzle.answer, "4")

    def test_correct_answer(self):
        result = self.puzzle.try_solve("4")
        self.assertTrue(self.puzzle.solved)
        self.assertIn("Correct", result)

    def test_wrong_answer(self):
        result = self.puzzle.try_solve("5")
        self.assertFalse(self.puzzle.solved)
        self.assertIn("Wrong", result)

    def test_case_insensitive_answer(self):
        puzzle = Puzzle("Question?", "echo", "Done.")
        puzzle.try_solve("ECHO")
        self.assertTrue(puzzle.solved)

    def test_already_solved(self):
        self.puzzle.try_solve("4")
        result = self.puzzle.try_solve("4")
        self.assertIn("Already solved", result)

    def test_required_item_missing(self):
        puzzle = Puzzle("Q?", "42", "Done.", required_item="Note")
        room = Room("R", "")
        player = Player(room)
        result = puzzle.try_solve("42", player)
        self.assertFalse(puzzle.solved)
        self.assertIn("Note", result)

    def test_required_item_present(self):
        puzzle = Puzzle("Q?", "42", "Done.", required_item="Note")
        room = Room("R", "")
        player = Player(room)
        player.inventory.append(Item("Note", "A note."))
        result = puzzle.try_solve("42", player)
        self.assertTrue(puzzle.solved)

    def test_no_required_item_no_player(self):
        result = self.puzzle.try_solve("4", player=None)
        self.assertTrue(self.puzzle.solved)

    def test_reward_in_result(self):
        result = self.puzzle.try_solve("4")
        self.assertIn("Correct!", result)


class TestNPC(unittest.TestCase):

    def setUp(self):
        tree = {
            "start": {
                "text": "Hello there.",
                "options": [
                    {"text": "Hi!", "next": "greet"},
                    {"text": "Bye.", "next": "farewell"},
                ]
            },
            "greet": {
                "text": "Nice to meet you.",
                "options": []
            },
            "farewell": {
                "text": "Goodbye.",
                "options": []
            }
        }
        self.npc = NPC("Stranger", tree)

    def test_initial_state(self):
        self.assertEqual(self.npc.state, "start")
        self.assertEqual(self.npc.name, "Stranger")

    def test_talk_shows_text(self):
        result = self.npc.talk()
        self.assertIn("Hello there.", result)

    def test_talk_shows_options(self):
        result = self.npc.talk()
        self.assertIn("Hi!", result)
        self.assertIn("Bye.", result)

    def test_choose_valid_option(self):
        self.npc.choose(1)
        self.assertEqual(self.npc.state, "greet")

    def test_choose_second_option(self):
        self.npc.choose(2)
        self.assertEqual(self.npc.state, "farewell")

    def test_choose_invalid_option(self):
        result = self.npc.choose(99)
        self.assertIn("Invalid", result)
        self.assertEqual(self.npc.state, "start")

    def test_choose_no_options_available(self):
        self.npc.choose(1)
        result = self.npc.choose(1)
        self.assertTrue(
            "Invalid" in result or "No choices" in result
        )

    def test_talk_terminal_node(self):
        self.npc.choose(1)
        result = self.npc.talk()
        self.assertIn("Nice to meet you.", result)

    def test_choose_with_result(self):
        tree = {
            "start": {
                "text": "Hello.",
                "options": [
                    {"text": "Wave.", "next": "wave", "result": "You wave back."}
                ]
            },
            "wave": {"text": "...", "options": []}
        }
        npc = NPC("Test", tree)
        result = npc.choose(1)
        self.assertEqual(result, "You wave back.")


class TestAchievements(unittest.TestCase):

    def setUp(self):
        self.ach = Achievements()

    def test_starts_empty(self):
        self.assertEqual(len(self.ach.unlocked), 0)

    def test_unlock(self):
        self.ach.unlock("First Steps")
        self.assertIn("First Steps", self.ach.unlocked)

    def test_unlock_duplicate(self):
        self.ach.unlock("First Steps")
        self.ach.unlock("First Steps")
        self.assertEqual(len(self.ach.unlocked), 1)

    def test_show_empty(self):
        result = self.ach.show()
        self.assertIn("No achievements", result)

    def test_show_with_achievements(self):
        self.ach.unlock("First Steps")
        self.ach.unlock("Explorer")
        result = self.ach.show()
        self.assertIn("First Steps", result)
        self.assertIn("Explorer", result)

    def test_multiple_achievements(self):
        names = ["A", "B", "C", "D"]
        for name in names:
            self.ach.unlock(name)
        self.assertEqual(len(self.ach.unlocked), 4)


class TestEndings(unittest.TestCase):

    def setUp(self):
        self.endings = Endings()

    def test_initial_state(self):
        self.assertIsNone(self.endings.current)

    def test_set_good(self):
        self.endings.set("good")
        self.assertEqual(self.endings.current, "good")

    def test_set_bad(self):
        self.endings.set("bad")
        self.assertEqual(self.endings.current, "bad")

    def test_set_secret(self):
        self.endings.set("secret")
        self.assertEqual(self.endings.current, "secret")

    def test_show_good(self):
        self.endings.set("good")
        result = self.endings.show()
        self.assertIn("GOOD", result)

    def test_show_bad(self):
        self.endings.set("bad")
        result = self.endings.show()
        self.assertIn("BAD", result)

    def test_show_secret(self):
        self.endings.set("secret")
        result = self.endings.show()
        self.assertIn("SECRET", result)

    def test_show_no_ending(self):
        result = self.endings.show()
        self.assertIn("No ending", result)


class TestSaveManager(unittest.TestCase):

    def setUp(self):
        self.game = Game()
        self.save_file = "test_save.json"

    def tearDown(self):
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
        if os.path.exists("save.json"):
            os.remove("save.json")

    def test_save_creates_file(self):
        SaveManager.save(self.game)
        self.assertTrue(os.path.exists("save.json"))

    def test_save_contains_room(self):
        SaveManager.save(self.game)
        with open("save.json") as f:
            data = json.load(f)
        self.assertIn("current_room", data)
        self.assertEqual(data["current_room"], "Cell")

    def test_save_contains_inventory(self):
        self.game.player.inventory.append(Item("Key", "A key."))
        SaveManager.save(self.game)
        with open("save.json") as f:
            data = json.load(f)
        self.assertIn("Key", data["inventory"])

    def test_save_contains_flags(self):
        self.game.flags["found_truth"] = True
        SaveManager.save(self.game)
        with open("save.json") as f:
            data = json.load(f)
        self.assertTrue(data["flags"]["found_truth"])

    def test_save_contains_achievements(self):
        self.game.achievements.unlock("Test")
        SaveManager.save(self.game)
        with open("save.json") as f:
            data = json.load(f)
        self.assertIn("Test", data["achievements"])

    def test_load_no_file(self):
        result = SaveManager.load()
        self.assertIsNone(result)

    def test_save_and_load_round_trip(self):
        self.game.flags["found_truth"] = True
        self.game.achievements.unlock("Puzzle Solver")
        SaveManager.save(self.game)

        game2 = Game()
        data = SaveManager.load()
        game2.apply_load(data)

        self.assertTrue(game2.flags["found_truth"])
        self.assertIn("Puzzle Solver", game2.achievements.unlocked)

    def test_apply_load_invalid_room(self):
        result = self.game.apply_load({"current_room": "NonExistent"})
        self.assertIn("unknown room", result)

    def test_apply_load_no_data(self):
        result = self.game.apply_load(None)
        self.assertIn("No save", result)

    def test_apply_load_restores_room(self):
        self.game.player.current_room = self.game.hall
        SaveManager.save(self.game)
        game2 = Game()
        game2.apply_load(SaveManager.load())
        self.assertEqual(game2.player.current_room.name, "Hall")



class TestGameWorld(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_all_rooms_exist(self):
        expected = ["Cell", "Hall", "Ventilation Shaft",
                    "Server Room", "Laboratory", "Exit"]
        for name in expected:
            self.assertIn(name, self.game.rooms)

    def test_player_starts_in_cell(self):
        self.assertEqual(self.game.player.current_room.name, "Cell")

    def test_cell_has_items(self):
        names = [i.name for i in self.game.cell.items]
        self.assertIn("Key", names)
        self.assertIn("Note", names)
        self.assertIn("VentTool", names)

    def test_hall_has_wire(self):
        names = [i.name for i in self.game.hall.items]
        self.assertIn("Wire", names)

    def test_vent_has_journal_page(self):
        names = [i.name for i in self.game.vent.items]
        self.assertIn("JournalPage", names)

    def test_server_room_has_items(self):
        names = [i.name for i in self.game.server_room.items]
        self.assertIn("KeycardFragment", names)
        self.assertIn("DataChip", names)

    def test_lab_has_items(self):
        names = [i.name for i in self.game.lab.items]
        self.assertIn("Battery", names)
        self.assertIn("AccessCard", names)

    def test_room_connections(self):
        self.assertIn("east", self.game.cell.connections)
        self.assertIn("west", self.game.hall.connections)
        self.assertIn("east", self.game.hall.connections)
        self.assertIn("north", self.game.hall.connections)
        self.assertIn("down", self.game.vent.connections)
        self.assertIn("east", self.game.server_room.connections)
        self.assertIn("east", self.game.lab.connections)

    def test_all_puzzles_exist(self):
        self.assertIsNotNone(self.game.cell.puzzle)
        self.assertIsNotNone(self.game.vent.puzzle)
        self.assertIsNotNone(self.game.server_room.puzzle)
        self.assertIsNotNone(self.game.lab.puzzle)
        self.assertIsNotNone(self.game.exit_room.puzzle)

    def test_flags_initialized(self):
        expected_flags = [
            "met_guard", "trusted_guard", "found_truth",
            "lab_unlocked", "vent_crawled", "server_hacked",
            "guard_alarmed", "scientist_met", "scientist_trusted",
            "exit_card_used", "exit_power_cut", "cell_unlocked"
        ]
        for flag in expected_flags:
            self.assertIn(flag, self.game.flags)
            self.assertFalse(self.game.flags[flag])


class TestGameMovement(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_cell_door_locked_initially(self):
        result = self.game.process("go east")
        self.assertIn("locked", result.lower())
        self.assertEqual(self.game.player.current_room.name, "Cell")

    def test_cell_door_opens_after_key(self):
        self.game.process("take Key")
        self.game.process("use Key")
        result = self.game.process("go east")
        self.assertEqual(self.game.player.current_room.name, "Hall")

    def test_vent_blocked_without_tool(self):
        self.game.flags["cell_unlocked"] = True
        self.game.player.current_room = self.game.hall
        result = self.game.process("go north")
        self.assertIn("bolted", result.lower())
        self.assertEqual(self.game.player.current_room.name, "Hall")

    def test_vent_opens_with_tool(self):
        self.game.player.current_room = self.game.hall
        self.game.player.inventory.append(Item("VentTool", ""))
        self.game.process("use VentTool")
        result = self.game.process("go north")
        self.assertEqual(self.game.player.current_room.name, "Ventilation Shaft")

    def test_exit_entry_dramatic_text(self):
        self.game.player.current_room = self.game.lab
        result = self.game.process("go east")
        self.assertIn("alarm", result.lower())
        self.assertEqual(self.game.player.current_room.name, "Exit")

    def test_invalid_direction(self):
        result = self.game.process("go west")
        self.assertIn("can't", result.lower())

    def test_go_without_direction(self):
        result = self.game.process("go")
        self.assertIn("where", result.lower())

    def test_vent_achievement_unlocked(self):
        self.game.player.current_room = self.game.hall
        self.game.player.inventory.append(Item("VentTool", ""))
        self.game.process("use VentTool")
        self.game.process("go north")
        self.assertIn("Air Crawler", self.game.achievements.unlocked)

    def test_vent_achievement_only_once(self):
        self.game.player.current_room = self.game.hall
        self.game.player.inventory.append(Item("VentTool", ""))
        self.game.process("use VentTool")
        self.game.process("go north")
        self.game.process("go south")
        self.game.process("go north")
        count = sum(1 for a in self.game.achievements.unlocked if a == "Air Crawler")
        self.assertEqual(count, 1)

    def test_scientist_met_flag_on_server_room_entry(self):
        self.game.player.current_room = self.game.vent
        self.game.process("go down")
        self.assertTrue(self.game.flags["scientist_met"])


class TestGameItemUsage(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def _give(self, *names):
        for name in names:
            self.game.player.inventory.append(Item(name, "test", usable=True))

    def test_use_key_unlocks_cell(self):
        self.game.process("take Key")
        result = self.game.process("use Key")
        self.assertIn("CLUNK", result)
        self.assertTrue(self.game.flags["cell_unlocked"])
        self.assertFalse(self.game.player.has_item("Key"))

    def test_use_key_already_unlocked(self):
        self.game.flags["cell_unlocked"] = True
        self._give("Key")
        result = self.game.process("use Key")
        self.assertIn("already", result.lower())
        self.assertTrue(self.game.player.has_item("Key"))

    def test_use_key_wrong_room(self):
        self.game.player.current_room = self.game.hall
        self._give("Key")
        result = self.game.process("use Key")
        self.assertIn("nothing", result.lower())
        self.assertTrue(self.game.player.has_item("Key"))

    def test_use_note_shows_riddle_not_answer(self):
        self.game.process("take Note")
        result = self.game.process("use Note")
        self.assertIn("corners of a square", result)
        self.assertNotIn("423", result)
        self.assertTrue(self.game.player.has_item("Note"))

    def test_use_wire_without_battery(self):
        self._give("Wire")
        result = self.game.process("use Wire")
        self.assertIn("Battery", result)
        self.assertTrue(self.game.player.has_item("Wire"))

    def test_use_wire_with_battery_in_lab(self):
        self.game.player.current_room = self.game.lab
        self._give("Wire", "Battery")
        result = self.game.process("use Wire")
        self.assertIn("terminal", result.lower())
        self.assertTrue(self.game.player.has_item("Wire"))

    def test_use_battery_without_wire(self):
        self._give("Battery")
        result = self.game.process("use Battery")
        self.assertIn("Wire", result)

    def test_use_venttool_in_hall(self):
        self.game.player.current_room = self.game.hall
        self._give("VentTool")
        result = self.game.process("use VentTool")
        self.assertIn("grate", result.lower())
        self.assertFalse(self.game.player.has_item("VentTool"))

    def test_use_venttool_wrong_room(self):
        self._give("VentTool")
        result = self.game.process("use VentTool")
        self.assertIn("nothing", result.lower())
        self.assertTrue(self.game.player.has_item("VentTool"))

    def test_use_keycard_without_fragment(self):
        self.game.player.current_room = self.game.exit_room
        self._give("AccessCard")
        result = self.game.process("use AccessCard")
        self.assertIn("REJECTED", result)
        self.assertTrue(self.game.player.has_item("AccessCard"))

    def test_use_keycard_with_fragment(self):
        self.game.player.current_room = self.game.exit_room
        self._give("AccessCard", "KeycardFragment")
        result = self.game.process("use AccessCard")
        self.assertTrue(self.game.flags["exit_card_used"])
        self.assertIn("CLICK", result)
        self.assertFalse(self.game.player.has_item("AccessCard"))

    def test_use_keycard_already_used(self):
        self.game.player.current_room = self.game.exit_room
        self.game.flags["exit_card_used"] = True
        self._give("AccessCard", "KeycardFragment")
        result = self.game.process("use AccessCard")
        self.assertIn("already", result.lower())

    def test_use_wire_cuts_exit_power(self):
        self.game.player.current_room = self.game.exit_room
        self.game.flags["exit_card_used"] = True
        self._give("Wire", "Battery")
        result = self.game.process("use Wire")
        self.assertTrue(self.game.flags["exit_power_cut"])
        self.assertIn("CRACK", result)
        self.assertFalse(self.game.player.has_item("Wire"))
        self.assertFalse(self.game.player.has_item("Battery"))

    def test_use_wire_before_card(self):
        self.game.player.current_room = self.game.exit_room
        self._give("Wire", "Battery")
        result = self.game.process("use Wire")
        self.assertFalse(self.game.flags["exit_power_cut"])
        self.assertIn("SEQUENCE ERROR", result)
        self.assertTrue(self.game.player.has_item("Wire"))
        self.assertTrue(self.game.player.has_item("Battery"))

    def test_use_datachip_lab_unlocked(self):
        self.game.player.current_room = self.game.lab
        self.game.flags["lab_unlocked"] = True
        self._give("DataChip")
        result = self.game.process("use DataChip")
        self.assertTrue(self.game.flags["found_truth"])
        self.assertIn("ECHO", result)
        self.assertFalse(self.game.player.has_item("DataChip"))

    def test_use_datachip_lab_locked(self):
        self.game.player.current_room = self.game.lab
        self._give("DataChip")
        result = self.game.process("use DataChip")
        self.assertFalse(self.game.flags["found_truth"])
        self.assertIn("offline", result.lower())
        self.assertTrue(self.game.player.has_item("DataChip"))

    def test_use_datachip_wrong_room(self):
        self.game.player.current_room = self.game.hall
        self._give("DataChip")
        result = self.game.process("use DataChip")
        self.assertIn("terminal", result.lower())
        self.assertTrue(self.game.player.has_item("DataChip"))

    def test_use_journal_page(self):
        self._give("JournalPage")
        result = self.game.process("use JournalPage")
        self.assertIn("7B3", result)
        self.assertTrue(self.game.player.has_item("JournalPage"))

    def test_use_nonexistent_item(self):
        result = self.game.process("use Sword")
        self.assertIn("don't have", result.lower())

    def test_use_without_item_name(self):
        result = self.game.process("use")
        self.assertIn("what", result.lower())

    def test_keycard_fragment_with_access_card(self):
        self._give("KeycardFragment", "AccessCard")
        result = self.game.process("use KeycardFragment")
        self.assertIn("restored", result.lower())
        self.assertFalse(self.game.player.has_item("KeycardFragment"))
        self.assertTrue(self.game.player.has_item("AccessCard"))

    def test_keycard_fragment_without_access_card(self):
        self._give("KeycardFragment")
        result = self.game.process("use KeycardFragment")
        self.assertIn("AccessCard", result)
        self.assertTrue(self.game.player.has_item("KeycardFragment"))


class TestGamePuzzles(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_cell_puzzle_wrong_answer(self):
        self.game.process("take Note")
        result = self.game.process("solve 999")
        self.assertIn("Wrong", result)
        self.assertFalse(self.game.cell.puzzle.solved)

    def test_cell_puzzle_correct_answer(self):
        self.game.process("take Note")
        result = self.game.process("solve 423")
        self.assertIn("Correct", result)
        self.assertTrue(self.game.cell.puzzle.solved)

    def test_cell_puzzle_requires_note(self):
        result = self.game.process("solve 423")
        self.assertIn("Note", result)
        self.assertFalse(self.game.cell.puzzle.solved)

    def test_vent_puzzle_correct(self):
        self.game.player.current_room = self.game.vent
        result = self.game.process("solve center")
        self.assertIn("Correct", result)
        self.assertTrue(self.game.vent.puzzle.solved)

    def test_server_puzzle_correct(self):
        self.game.player.current_room = self.game.server_room
        result = self.game.process("solve 7b3")
        self.assertIn("Correct", result)
        self.assertTrue(self.game.server_room.puzzle.solved)
        self.assertTrue(self.game.flags["server_hacked"])

    def test_server_puzzle_unlocks_achievement(self):
        self.game.player.current_room = self.game.server_room
        self.game.process("solve 7b3")
        self.assertIn("Ghost in the Machine", self.game.achievements.unlocked)

    def test_lab_puzzle_correct(self):
        self.game.player.current_room = self.game.lab
        self.game.player.inventory.append(Item("Battery", ""))
        result = self.game.process("solve echo")
        self.assertIn("Correct", result)
        self.assertTrue(self.game.flags["lab_unlocked"])

    def test_exit_puzzle_blocked_without_locks(self):
        self.game.player.current_room = self.game.exit_room
        result = self.game.process("solve echo")
        self.assertIn("Lock 1", result)
        self.assertFalse(self.game.exit_room.puzzle.solved)

    def test_exit_puzzle_blocked_without_lock2(self):
        self.game.player.current_room = self.game.exit_room
        self.game.flags["exit_card_used"] = True
        result = self.game.process("solve echo")
        self.assertIn("Lock 2", result)

    def test_exit_puzzle_correct_after_locks(self):
        self.game.player.current_room = self.game.exit_room
        self.game.flags["exit_card_used"] = True
        self.game.flags["exit_power_cut"] = True
        result = self.game.process("solve echo")
        self.assertIn("Correct", result)
        self.assertTrue(self.game.exit_room.puzzle.solved)

    def test_puzzle_command_no_puzzle(self):
        self.game.player.current_room = self.game.hall
        result = self.game.process("puzzle")
        self.assertIn("No puzzle", result)

    def test_puzzle_command_shows_question(self):
        result = self.game.process("puzzle")
        self.assertIn("Square", result)

    def test_solve_no_puzzle_room(self):
        self.game.player.current_room = self.game.hall
        result = self.game.process("solve anything")
        self.assertIn("No puzzle", result)

    def test_puzzle_solver_achievement(self):
        self.game.player.current_room = self.game.vent
        self.game.process("solve center")
        self.assertIn("Puzzle Solver", self.game.achievements.unlocked)


class TestGameNPCs(unittest.TestCase):

    def setUp(self):
        self.game = Game()
        self.game.player.current_room = self.game.hall

    def test_talk_guard_in_hall(self):
        result = self.game.process("talk")
        self.assertIn("Guard", result)
        self.assertTrue(self.game.flags["met_guard"])

    def test_talk_no_npc(self):
        self.game.player.current_room = self.game.cell
        result = self.game.process("talk")
        self.assertIn("no one", result.lower())

    def test_guard_silent_path_sets_trusted(self):
        self.game.process("talk")
        self.game.process("choose 4")
        self.assertTrue(self.game.flags["trusted_guard"])

    def test_guard_exit_hint_sets_trusted(self):
        self.game.process("talk")
        self.game.process("choose 2")
        self.game.process("choose 2")
        self.assertTrue(self.game.flags["trusted_guard"])

    def test_guard_researcher_path_sets_truth(self):
        self.game.process("talk")
        self.game.process("choose 1")
        self.game.process("choose 1")
        self.game.process("choose 2")
        self.game.process("choose 1")
        self.assertTrue(self.game.flags["found_truth"])
        self.assertIn("Truth Seeker", self.game.achievements.unlocked)

    def test_guard_zero_path_sets_truth(self):
        self.game.process("talk")
        self.game.process("choose 2")
        self.game.process("choose 3")
        self.game.process("choose 1")
        self.assertTrue(self.game.flags["found_truth"])

    def test_guard_alarm_bad_ending(self):
        self.game.process("talk")
        self.game.process("choose 3")
        self.game.process("choose 2")
        self.game.process("choose 2")
        self.assertTrue(self.game.flags["guard_alarmed"])
        self.assertFalse(self.game.running)
        self.assertEqual(self.game.endings.current, "bad")

    def test_guard_alarm_stopped(self):
        self.game.process("talk")
        self.game.process("choose 3")
        self.game.process("choose 2")
        self.game.process("choose 1")
        self.game.process("choose 1")
        self.assertFalse(self.game.flags["guard_alarmed"])
        self.assertTrue(self.game.running)

    def test_scientist_talk_in_server_room(self):
        self.game.player.current_room = self.game.server_room
        result = self.game.process("talk")
        self.assertIn("Scientist", result)

    def test_scientist_identity_sets_truth(self):
        self.game.player.current_room = self.game.server_room
        self.game.process("talk")
        self.game.process("choose 1")
        self.game.process("choose 3")
        self.assertTrue(self.game.flags["scientist_trusted"])

    def test_scientist_still_here_sets_truth(self):
        self.game.player.current_room = self.game.server_room
        self.game.process("talk")
        self.game.process("choose 1")
        self.game.process("choose 1")
        self.game.process("choose 1")
        self.game.process("choose 1")
        self.assertTrue(self.game.flags["found_truth"])

    def test_choose_invalid_number(self):
        result = self.game.process("choose abc")
        self.assertIn("Invalid", result)

    def test_choose_without_number(self):
        result = self.game.process("choose")
        self.assertIn("which", result.lower())


class TestGameEndings(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def _reach_exit_and_unlock(self):
        self.game.player.current_room = self.game.exit_room
        self.game.flags["exit_card_used"] = True
        self.game.flags["exit_power_cut"] = True

    def test_good_ending(self):
        self._reach_exit_and_unlock()
        self.game.process("solve echo")
        self.game.check_endings()
        self.assertEqual(self.game.endings.current, "good")
        self.assertFalse(self.game.running)

    def test_secret_ending(self):
        self.game.flags["found_truth"] = True
        self._reach_exit_and_unlock()
        self.game.process("solve echo")
        self.game.check_endings()
        self.assertEqual(self.game.endings.current, "secret")
        self.assertFalse(self.game.running)

    def test_bad_ending_via_alarm(self):
        self.game.player.current_room = self.game.hall
        self.game.process("talk")
        self.game.process("choose 3")
        self.game.process("choose 2")
        self.game.process("choose 2")
        self.assertEqual(self.game.endings.current, "bad")
        self.assertFalse(self.game.running)

    def test_bad_ending_via_failed_attempts(self):
        self.game.player.current_room = self.game.exit_room
        self.game.flags["exit_card_used"] = True
        self.game.flags["exit_power_cut"] = True
        self.game.process("solve wrong1")
        self.game.process("solve wrong2")
        self.game.process("solve wrong3")
        self.assertEqual(self.game.endings.current, "bad")
        self.assertFalse(self.game.running)

    def test_failed_attempts_counted(self):
        self.game.player.current_room = self.game.exit_room
        self.game.flags["exit_card_used"] = True
        self.game.flags["exit_power_cut"] = True
        self.game.process("solve wrong1")
        self.assertEqual(self.game.failed_attempts, 1)
        self.game.process("solve wrong2")
        self.assertEqual(self.game.failed_attempts, 2)

    def test_no_ending_before_exit_solved(self):
        self.game.player.current_room = self.game.exit_room
        self.game.check_endings()
        self.assertIsNone(self.game.endings.current)
        self.assertTrue(self.game.running)

    def test_check_endings_not_in_exit_room(self):
        self.game.player.current_room = self.game.lab
        self.game.check_endings()
        self.assertTrue(self.game.running)

class TestGameCommands(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_look_command(self):
        result = self.game.process("look")
        self.assertIn("Exits", result)
        self.assertIn("Items", result)

    def test_items_command(self):
        result = self.game.process("items")
        self.assertIn("Key", result)

    def test_take_command(self):
        result = self.game.process("take Key")
        self.assertIn("Key", result)
        self.assertTrue(self.game.player.has_item("Key"))

    def test_inv_command_empty(self):
        result = self.game.process("inv")
        self.assertIn("empty", result.lower())

    def test_inv_command_with_items(self):
        self.game.process("take Key")
        result = self.game.process("inv")
        self.assertIn("Key", result)

    def test_inspect_inventory_item(self):
        self.game.process("take Key")
        result = self.game.process("inspect Key")
        self.assertIn("Key", result)

    def test_inspect_room_item(self):
        result = self.game.process("inspect Key")
        self.assertIn("Key", result)

    def test_inspect_nonexistent(self):
        result = self.game.process("inspect Sword")
        self.assertIn("don't see", result.lower())

    def test_achievements_command_empty(self):
        result = self.game.process("achievements")
        self.assertIn("No achievements", result)

    def test_achievements_command_with_unlocked(self):
        self.game.achievements.unlock("Test Achievement")
        result = self.game.process("achievements")
        self.assertIn("Test Achievement", result)

    def test_status_in_exit_room(self):
        self.game.player.current_room = self.game.exit_room
        result = self.game.process("status")
        self.assertIn("LOCK", result)

    def test_status_not_in_exit_room(self):
        result = self.game.process("status")
        self.assertIn("Nothing", result)

    def test_help_command(self):
        result = self.game.process("help")
        self.assertIn("go", result)
        self.assertIn("look", result)
        self.assertIn("solve", result)

    def test_quit_command(self):
        result = self.game.process("quit")
        self.assertFalse(self.game.running)

    def test_empty_command(self):
        result = self.game.process("")
        self.assertEqual(result, "")

    def test_unknown_command(self):
        result = self.game.process("fly")
        self.assertIn("Unknown", result)

    def test_save_command(self):
        result = self.game.process("save")
        self.assertIn("saved", result.lower())
        self.assertTrue(os.path.exists("save.json"))
        os.remove("save.json")

    def test_load_no_save(self):
        if os.path.exists("save.json"):
            os.remove("save.json")
        result = self.game.process("load")
        self.assertIn("No save", result)

    def test_look_in_exit_room_shows_status(self):
        self.game.player.current_room = self.game.exit_room
        result = self.game.process("look")
        self.assertIn("LOCK", result)

    def test_take_without_name(self):
        result = self.game.process("take")
        self.assertIn("what", result.lower())

    def test_use_without_name(self):
        result = self.game.process("use")
        self.assertIn("what", result.lower())

    def test_inspect_without_name(self):
        result = self.game.process("inspect")
        self.assertIn("what", result.lower())

class TestEscapePygameGUI(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.gui = EscapePygameGUI()

    def tearDown(self):
        pygame.quit()

    def test_initial_state(self):
        self.assertEqual(self.gui.game.player.current_room.name, "Cell")
        self.assertTrue(len(self.gui.output_lines) > 0)

    def test_welcome_message_exists(self):
        text = " ".join(line for line, _ in self.gui.output_lines)
        self.assertIn("ESCAPE PYTHON", text)

    def test_submit_empty_command(self):
        self.gui.input_text = ""
        self.gui._submit()
        self.assertEqual(self.gui.input_text, "")

    def test_submit_look_command(self):
        self.gui.input_text = "look"
        self.gui._submit()

        outputs = [t for t, _ in self.gui.output_lines]
        self.assertTrue(any("look" in o.lower() for o in outputs))

    def test_submit_go_executes_without_crash(self):
        self.gui.input_text = "go east"
        self.gui._submit()
        self.assertTrue(len(self.gui.output_lines) > 0)

    def test_history_is_stored(self):
        self.gui.input_text = "look"
        self.gui._submit()

        self.assertIn("look", self.gui.history)

    def test_history_navigation_up(self):
        self.gui.history = ["look", "go east"]
        self.gui.history_pos = -1

        event = type("E", (), {"key": pygame.K_UP})
        self.gui._handle_key(event)

        self.assertEqual(self.gui.input_text, "go east")

    def test_history_navigation_down(self):
        self.gui.history = ["look", "go east"]
        self.gui.history_pos = 1
        self.gui.input_text = "go east"

        event = type("E", (), {"key": pygame.K_DOWN})
        self.gui._handle_key(event)

        self.assertIn(self.gui.input_text, ["look", ""])

    def test_escape_clears_input(self):
        self.gui.input_text = "something"

        event = type("E", (), {"key": pygame.K_ESCAPE})
        self.gui._handle_key(event)

        self.assertEqual(self.gui.input_text, "")

    def test_backspace_removes_char(self):
        self.gui.input_text = "abc"

        event = type("E", (), {"key": pygame.K_BACKSPACE})
        self.gui._handle_key(event)

        self.assertEqual(self.gui.input_text, "ab")

    def test_visited_rooms_tracking(self):
        self.gui.input_text = "go east"
        self.gui._submit()

        current = self.gui.game.player.current_room.name
        self.assertIn(current, self.gui.visited)

    def test_particles_spawn_on_movement(self):
        self.gui.input_text = "go east"
        self.gui._submit()
        self.assertIsInstance(self.gui.particles, list)

    def test_output_buffer_limit(self):
        for i in range(500):
            self.gui._print(f"line {i}")

        self.assertLessEqual(len(self.gui.output_lines), 400)

    def test_draw_map_no_crash(self):
        self.gui._draw_map()

    def test_draw_panel_no_crash(self):
        self.gui._draw_panel()

    def test_update_particles_no_crash(self):
        self.gui._update_particles()

if __name__ == "__main__":
    unittest.main(verbosity=2)