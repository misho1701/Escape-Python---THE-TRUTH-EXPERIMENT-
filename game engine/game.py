from room import Room
from player import Player
from item import Item
from puzzle import Puzzle
from npc import NPC
from achievements import Achievements
from endings import Endings
from save_manager import SaveManager


class Game:

    def __init__(self):

        self.rooms = {}
        self.running = True

        self.achievements = Achievements()
        self.endings = Endings()

        self.failed_attempts = 0

        self.flags = {
            "met_guard": False,
            "trusted_guard": False,
            "found_truth": False,
            "lab_unlocked": False,
            "vent_crawled": False,
            "server_hacked": False,
            "guard_alarmed": False,
            "scientist_met": False,
            "scientist_trusted": False,
            # Exit door locks
            "exit_card_used": False,
            "exit_power_cut": False,
            # Cell door
            "cell_unlocked": False,
        }

        self.create_world()

    def create_world(self):

        # ---------- ROOMS ----------

        self.cell = Room(
            "Cell",
            """
You wake up inside a cold prison cell.

The air is damp and heavy.
A rusty bed stands against the wall.
A broken desk is covered in dust.

Something glints beneath the bed —
a key, a crumpled note, and what looks like a screwdriver.
"""
        )

        self.hall = Room(
            "Hall",
            """
A narrow corridor stretches ahead.

The lights flicker constantly.
Old warning signs hang from the walls.

A ventilation grate is bolted to the north wall.
"""
        )

        self.vent = Room(
            "Ventilation Shaft",
            """
You squeeze through a network of dusty metal ducts.

The air tastes stale and metallic.
Strange humming echoes from somewhere below.

A faded label on the duct wall reads: SECTOR 7-B.
A torn piece of paper is wedged into a corner of the duct.
There is a loose panel to the south that leads somewhere new.
"""
        )

        self.server_room = Room(
            "Server Room",
            """
Rows of humming server racks fill the room.

Blinking LEDs cast a cold blue glow.
A console terminal sits in the corner, still running.

A woman sits hunched against the far wall, arms around her knees.
She looks up when you enter.
"""
        )

        self.lab = Room(
            "Laboratory",
            """
A forgotten laboratory.

Broken monitors flicker with corrupted data.
A terminal seems to still have power.
"""
        )

        self.exit_room = Room(
            "Exit",
            """
The alarm cut off the moment you stepped inside.

A massive reinforced steel door looms before you.
Three distinct locking mechanisms are visible:

  [LOCK 1] Card reader — slot glowing RED
  [LOCK 2] Power conduit — magnetic seal ACTIVE
  [LOCK 3] Logic gate — panel DARK, waiting

Disable each lock in order to open the door.
Type 'status' to check lock progress at any time.
"""
        )

        self.cell.connect("east", self.hall)

        self.hall.connect("west", self.cell)
        self.hall.connect("east", self.lab)
        self.hall.connect("north", self.vent)

        self.vent.connect("south", self.hall)
        self.vent.connect("down", self.server_room)

        self.server_room.connect("up", self.vent)
        self.server_room.connect("east", self.lab)

        self.lab.connect("west", self.hall)
        self.lab.connect("east", self.exit_room)

        self.exit_room.connect("west", self.lab)

        key = Item(
            "Key",
            "A rusty key. It might open something nearby.",
            item_type="key",
            usable=True,
            hint="Try using this near a locked door."
        )

        note = Item(
            "Note",
            "A crumpled note with numbers encoded as riddles.",
            item_type="hint",
            usable=True,
            hint=(
                "Square corners = 4. "
                "Bicycle wheels = 2. "
                "Triangle sides = 3. "
                "Code: 423"
            )
        )

        wire = Item(
            "Wire",
            "A thin electrical wire. Could conduct power between components.",
            item_type="tool",
            usable=True,
            hint="Combine with Battery to power something."
        )

        battery = Item(
            "Battery",
            "A partially charged battery. Still has juice.",
            item_type="tool",
            usable=True,
            hint="Pair with the Wire to activate electronics."
        )

        access_card = Item(
            "AccessCard",
            "A magnetic security card. Smells faintly of coffee.",
            item_type="key",
            usable=True,
            hint="Swipe this at a card reader to open secure doors."
        )

        vent_tool = Item(
            "VentTool",
            "A flat-head screwdriver left inside the shaft.",
            item_type="tool",
            usable=True,
            hint="Useful for prying open panels or unscrewing bolts."
        )

        keycard_fragment = Item(
            "KeycardFragment",
            "Half of a broken security keycard. The chip still looks intact.",
            item_type="key",
            usable=True,
            hint="Combine with AccessCard to restore full access privileges."
        )

        data_chip = Item(
            "DataChip",
            "A small memory chip pulled from a server rack. Data encrypted.",
            item_type="misc",
            usable=True,
            hint="Insert into the lab terminal to decrypt classified files."
        )

        journal_page = Item(
            "JournalPage",
            "A torn page from someone's personal log. The handwriting is frantic.",
            item_type="hint",
            usable=True,
            hint=(
                "The page reads:\n"
                "  '...moved to Sector 7B after the Level 3 incident.\n"
                "   New ID format they gave us: sector letters + level number.\n"
                "   Mine was 7B3. I hope nobody finds this.'"
            )
        )

        self.cell.add_item(key)
        self.cell.add_item(note)
        self.cell.add_item(vent_tool)

        self.hall.add_item(wire)

        self.vent.add_item(journal_page)

        self.server_room.add_item(keycard_fragment)
        self.server_room.add_item(data_chip)

        self.lab.add_item(battery)
        self.lab.add_item(access_card)

        self.cell.puzzle = Puzzle(
            """
A note says:

  Square has how many corners?
  Bicycle has how many wheels?
  Triangle has how many sides?

Enter code:
""",
            "423",
            "Door mechanism unlocked.",
            required_item="Note"
        )

        self.vent.puzzle = Puzzle(
            """
A rusted latch seals the panel to the server room below.

The mechanism has three positions: LEFT, CENTER, RIGHT.

A scratched inscription reads:
  'Where the needle rests at midnight.'

Enter position:
""",
            "center",
            "The panel swings open. Cold air rushes up from below.",
        )

        self.server_room.puzzle = Puzzle(
            """
The console terminal prompts:

  > AUTHENTICATION REQUIRED
  > Enter employee ID prefix: __

A sticky note on the rack reads:
  'ID format: first 2 letters of sector + level'
  Sector: 7B, Level: 3

Enter ID:
""",
            "7b3",
            "Access granted. Classified files unlocked. A DataChip ejects from the slot.",
        )

        self.lab.puzzle = Puzzle(
            """
Terminal requires activation.

Hint: energy + access system required.
""",
            "echo",
            "Terminal activated. Files begin to decrypt...",
            required_item="Battery"
        )

        self.exit_room.puzzle = Puzzle(
            """
LOCK 3 — LOGIC GATE ACTIVE

The panel flickers on, displaying a final challenge:

  "I speak without a mouth and hear without ears.
   I have no body, but I come alive with the wind.
   What am I?"

The cursor blinks. One chance. Choose your words carefully.
""",
            "echo",
            "LOCK 3 DISENGAGED.\nAll systems nominal. The door is yours."
        )

        guard_tree = {

            "start": {
                "text": (
                    "Guard: *startled* You're awake? You shouldn't be.\n"
                    "       They said the sedative would last until morning."
                ),
                "options": [
                    {"text": "Who are you?",              "next": "who"},
                    {"text": "Where am I?",               "next": "where"},
                    {"text": "Get me out of here. Now.",  "next": "demand"},
                    {"text": "...",                       "next": "silent"},
                ]
            },

            "who": {
                "text": (
                    "Guard: *lowers voice* My name doesn't matter.\n"
                    "       I've worked here three years. I used to believe in the project.\n"
                    "       Now... I'm not sure what I believe."
                ),
                "options": [
                    {"text": "What project?",            "next": "project"},
                    {"text": "You sound guilty.",        "next": "guilt"},
                    {"text": "Help me escape.",          "next": "help_ask"},
                ]
            },

            "where": {
                "text": (
                    "Guard: Underground research facility. Sector 7.\n"
                    "       We're sixty metres below the surface.\n"
                    "       Nobody knows this place exists."
                ),
                "options": [
                    {"text": "Who built this place?",    "next": "built"},
                    {"text": "How do I get out?",        "next": "exit_hint"},
                    {"text": "What am I doing here?",    "next": "subject"},
                ]
            },

            "demand": {
                "text": (
                    "Guard: *steps back* Keep your voice down.\n"
                    "       If the cameras pick up movement in this block,\n"
                    "       we're both finished."
                ),
                "options": [
                    {"text": "Then help me quietly.",    "next": "help_ask"},
                    {"text": "I don't care. Open it.",   "next": "threaten"},
                    {"text": "Sorry. I'm scared.",       "next": "apologise"},
                ]
            },

            "silent": {
                "text": (
                    "Guard: *watches you carefully*\n"
                    "       Smart. The walls have ears here.\n"
                    "       *slips something under the door*\n"
                    "       That key opens the east corridor. Use it wisely."
                ),
                "options": [],
                "flag": "trusted_guard"
            },

            "project": {
                "text": (
                    "Guard: Project ECHO. Memory reconstruction research.\n"
                    "       They said it was voluntary. It wasn't.\n"
                    "       The subjects didn't know who they were before they arrived."
                ),
                "options": [
                    {"text": "Am I one of the subjects?",    "next": "subject"},
                    {"text": "Who ran the project?",         "next": "who_ran"},
                ]
            },

            "guilt": {
                "text": (
                    "Guard: *long pause*\n"
                    "       I reported what I saw once. They transferred me to night shift.\n"
                    "       After that I stopped asking questions.\n"
                    "       I should have kept asking."
                ),
                "options": [
                    {"text": "It's not too late.",       "next": "help_ask"},
                    {"text": "You're complicit.",        "next": "accuse"},
                ]
            },

            "built": {
                "text": (
                    "Guard: A private research group. Government contract.\n"
                    "       The lead researcher designed the whole thing.\n"
                    "       Brilliant person. Completely lost their mind by year two."
                ),
                "options": [
                    {"text": "What happened to the researcher?", "next": "researcher"},
                ]
            },

            "exit_hint": {
                "text": (
                    "Guard: The main door needs a card, a power bypass, and a passphrase.\n"
                    "       The passphrase is the name of the project.\n"
                    "       *glances at camera* That's all I can say."
                ),
                "options": [],
                "flag": "trusted_guard"
            },

            "subject": {
                "text": (
                    "Guard: *can't meet your eyes*\n"
                    "       Subject zero. The first one.\n"
                    "       You weren't supposed to wake up this lucid."
                ),
                "options": [
                    {"text": "Subject zero — what does that mean?", "next": "zero"},
                ]
            },

            "help_ask": {
                "text": (
                    "Guard: I can't open the door. My clearance was revoked last week.\n"
                    "       But there are ways out that aren't on the official map.\n"
                    "       Check the ventilation system. And find the lab terminal."
                ),
                "options": [],
                "flag": "trusted_guard"
            },

            "threaten": {
                "text": (
                    "Guard: *expression hardens*\n"
                    "       You just made a mistake.\n"
                    "       *reaches for the alarm panel*"
                ),
                "options": [
                    {"text": "Wait — stop!", "next": "alarm_stop"},
                    {"text": "Do it then.",  "next": "alarm_trigger"},
                ]
            },

            "apologise": {
                "text": (
                    "Guard: *softens slightly*\n"
                    "       It's okay. I'd be scared too.\n"
                    "       Listen — I want to help. But I can't be seen doing it."
                ),
                "options": [
                    {"text": "What can you tell me?",    "next": "exit_hint"},
                ]
            },

            "accuse": {
                "text": (
                    "Guard: *jaw tightens*\n"
                    "       Yes. I am.\n"
                    "       And I have to live with that.\n"
                    "       Don't push me further."
                ),
                "options": [
                    {"text": "Help me and make it right.", "next": "help_ask"},
                    {"text": "I'm done talking.",          "next": "done"},
                ]
            },

            "who_ran": {
                "text": (
                    "Guard: The lead researcher. Brilliant. Obsessive.\n"
                    "       They called the project ECHO because of something they said:\n"
                    "       'Memory is just an echo of who we used to be.'"
                ),
                "options": [
                    {"text": "What happened to them?",   "next": "researcher"},
                ]
            },

            "researcher": {
                "text": (
                    "Guard: *hesitates*\n"
                    "       They disappeared. Six months ago.\n"
                    "       Some say they were the first test subject.\n"
                    "       *stares at you*\n"
                    "       You have their eyes."
                ),
                "options": [],
                "flag": "found_truth"
            },

            "zero": {
                "text": (
                    "Guard: Subject zero was the researcher themselves.\n"
                    "       They volunteered first. Said it was the only ethical thing to do.\n"
                    "       The memory wipe worked too well. They forgot everything.\n"
                    "       Even that they built this place."
                ),
                "options": [],
                "flag": "found_truth"
            },

            "alarm_stop": {
                "text": (
                    "Guard: *hand hovers over the panel*\n"
                    "       Give me one reason."
                ),
                "options": [
                    {"text": "I just want to go home.",      "next": "alarm_mercy"},
                    {"text": "I'll tell them you helped me.", "next": "alarm_trigger"},
                ]
            },

            "alarm_mercy": {
                "text": (
                    "Guard: *slowly lowers hand*\n"
                    "       ...\n"
                    "       Get out of here. And don't look back."
                ),
                "options": [],
                "flag": "trusted_guard"
            },

            "alarm_trigger": {
                "text": (
                    "Guard: *slams the alarm*\n\n"
                    "RED LIGHTS FLOOD THE CORRIDOR.\n"
                    "A siren WAILS through the facility.\n\n"
                    "Guard: You brought this on yourself."
                ),
                "options": [],
                "flag": "guard_alarmed"
            },

            "done": {
                "text": (
                    "Guard: *turns away*\n"
                    "       Then we're done here."
                ),
                "options": []
            },
        }

        self.guard = NPC("Guard", guard_tree)

        scientist_tree = {

            "start": {
                "text": (
                    "Scientist: *looks up with hollow eyes*\n"
                    "           Oh. Another one of them let you out?\n"
                    "           Or did you get out yourself?"
                ),
                "options": [
                    {"text": "I got out myself. Who are you?",  "next": "who"},
                    {"text": "Are you trapped too?",            "next": "trapped"},
                    {"text": "I need help getting out.",        "next": "help"},
                ]
            },

            "who": {
                "text": (
                    "Scientist: Dr. Voss. Junior researcher, Project ECHO.\n"
                    "           I was supposed to leave six months ago.\n"
                    "           They said the exit was 'temporarily sealed'.\n"
                    "           I stopped believing that around month three."
                ),
                "options": [
                    {"text": "What is Project ECHO?",           "next": "echo"},
                    {"text": "Can you help me escape?",         "next": "help"},
                    {"text": "Do you know who I am?",           "next": "identity"},
                ]
            },

            "trapped": {
                "text": (
                    "Scientist: Since the lockdown, yes.\n"
                    "           I have food from the supply cache. Power from the servers.\n"
                    "           What I don't have is a working keycard.\n"
                    "           Mine shattered when I dropped it."
                ),
                "options": [
                    {"text": "I might be able to help with that.", "next": "card_offer"},
                    {"text": "Tell me about this place.",          "next": "echo"},
                ]
            },

            "help": {
                "text": (
                    "Scientist: The exit door has three locks.\n"
                    "           Card reader, power conduit, and a logic gate.\n"
                    "           The logic gate answer is the name of this project.\n"
                    "           Four letters. Think about what an echo is."
                ),
                "options": [
                    {"text": "Thank you. One more thing...",     "next": "identity"},
                    {"text": "What about the card reader?",      "next": "card_hint"},
                ]
            },

            "echo": {
                "text": (
                    "Scientist: Memory reconstruction. They could erase specific memories\n"
                    "           and replace them. Or just... wipe everything.\n"
                    "           The lead researcher called it 'giving people a clean slate'.\n"
                    "           I called it a human rights violation."
                ),
                "options": [
                    {"text": "Who was the lead researcher?",     "next": "researcher"},
                    {"text": "Were the subjects willing?",       "next": "willing"},
                ]
            },

            "identity": {
                "text": (
                    "Scientist: *studies your face*\n"
                    "           I thought so when you walked in.\n"
                    "           You're not just a subject.\n"
                    "           There's a DataChip in these servers. Find it.\n"
                    "           Read it in the lab. Then you'll know."
                ),
                "options": [],
                "flag": "scientist_trusted"
            },

            "card_offer": {
                "text": (
                    "Scientist: *stands up slowly*\n"
                    "           The fragment is behind rack seven. I couldn't reach it.\n"
                    "           If you have an AccessCard, the two pieces bond together —\n"
                    "           the chips are paired. Same batch."
                ),
                "options": [
                    {"text": "I'll look for it.",               "next": "card_thanks"},
                ]
            },

            "card_hint": {
                "text": (
                    "Scientist: You need an AccessCard — there's one in the lab.\n"
                    "           But it's broken. The fragment that completes it\n"
                    "           is somewhere in this room."
                ),
                "options": [
                    {"text": "Got it. What about the passphrase?", "next": "help"},
                ]
            },

            "researcher": {
                "text": (
                    "Scientist: The most brilliant person I've ever met.\n"
                    "           And the most reckless.\n"
                    "           They went through the procedure themselves.\n"
                    "           Voluntarily. First subject.\n"
                    "           We never saw them again after that."
                ),
                "options": [
                    {"text": "Do you think they're still here?", "next": "still_here"},
                ]
            },

            "willing": {
                "text": (
                    "Scientist: At first. The early subjects signed consent forms.\n"
                    "           Then the funding ran out and the forms... stopped.\n"
                    "           I raised concerns. They locked down the facility.\n"
                    "           That was six months ago."
                ),
                "options": [
                    {"text": "Who was funding this?",           "next": "funding"},
                ]
            },

            "still_here": {
                "text": (
                    "Scientist: *very quietly*\n"
                    "           Yes.\n"
                    "           I think they're standing right in front of me."
                ),
                "options": [],
                "flag": "found_truth"
            },

            "funding": {
                "text": (
                    "Scientist: Government black budget. No paper trail.\n"
                    "           When I tried to document it, my files were deleted.\n"
                    "           These servers hold the only remaining copies.\n"
                    "           That's why I've been protecting them."
                ),
                "options": []
            },

            "card_thanks": {
                "text": (
                    "Scientist: Be careful out there.\n"
                    "           And if you make it out...\n"
                    "           tell someone what happened here."
                ),
                "options": []
            },
        }

        self.scientist = NPC("Scientist", scientist_tree)

        self.rooms = {
            "Cell": self.cell,
            "Hall": self.hall,
            "Ventilation Shaft": self.vent,
            "Server Room": self.server_room,
            "Laboratory": self.lab,
            "Exit": self.exit_room,
        }

        self.player = Player(self.cell)

    def help(self):

        return """
=============================
AVAILABLE COMMANDS
=============================

Movement:
  go <direction>     east / west / north / south / up / down

Exploration:
  look               describe current room
  items              list items in room

Inventory:
  take <item>        pick up an item
  inv                show your inventory
  use <item>         use an item from inventory
  inspect <item>     examine an item closely

NPC:
  talk               speak to an NPC in the room
  choose <number>    pick a dialogue option

Puzzles:
  puzzle             show the current room's puzzle
  solve <answer>     attempt to solve the puzzle
  status             show exit door lock status (in Exit room)

System:
  save               save the game
  load               load the game
  achievements       show unlocked achievements
  help               show this menu
  quit               exit the game
=============================
"""

    def exit_status(self):

        def mark(done):
            return "GREEN  ✓" if done else "RED    ✗"

        lock3_done = self.exit_room.puzzle.solved

        lines = [
            "=============================",
            "   EXIT DOOR — LOCK STATUS",
            "=============================",
            f"  LOCK 1  Card Reader    [{mark(self.flags['exit_card_used'])}]",
            f"  LOCK 2  Power Conduit  [{mark(self.flags['exit_power_cut'])}]",
            f"  LOCK 3  Logic Gate     [{mark(lock3_done)}]",
            "=============================",
        ]

        if not self.flags["exit_card_used"]:
            lines.append("→ Use your AccessCard on the card reader.")
        elif not self.flags["exit_power_cut"]:
            lines.append("→ Cut the magnetic seal. Use Wire + Battery together.")
        elif not lock3_done:
            lines.append("→ Logic gate is live. Type 'puzzle' to read the riddle.")
        else:
            lines.append("→ All locks cleared. The door is open.")

        return "\n".join(lines)

    def process(self, command):

        parts = command.split()

        if not parts:
            return ""

        action = parts[0].lower()

        if action == "go":

            if len(parts) < 2:
                return "Go where?"

            direction = parts[1].lower()
            room = self.player.current_room

            if room == self.cell and direction == "east":
                if not self.flags["cell_unlocked"]:
                    return (
                        "The cell door is locked.\n"
                        "You rattle it — solid. There must be a way to open it.\n"
                        "Hint: you picked up something that might help."
                    )

            if room == self.hall and direction == "north":
                if not self.player.has_item("VentTool"):
                    return (
                        "The ventilation grate is bolted shut.\n"
                        "You need something to unscrew it."
                    )

            if room == self.lab and direction == "east":
                result = self.player.move(direction)
                if self.player.current_room == self.exit_room:
                    result = (
                        "You push through the laboratory door.\n\n"
                        "Instantly, a deafening alarm BLARES.\n"
                        "Red emergency lights flood the corridor.\n\n"
                        "A synthesized voice crackles through the speakers:\n"
                        "  'UNAUTHORIZED ACCESS DETECTED. LOCKDOWN INITIATED.'\n\n"
                        "The alarm cuts out. Silence.\n"
                        "The door behind you seals with a heavy CLUNK.\n\n"
                        + self.exit_room.description
                    )
                return result

            result = self.player.move(direction)

            if self.player.current_room == self.vent and not self.flags["vent_crawled"]:
                self.flags["vent_crawled"] = True
                self.achievements.unlock("Air Crawler")
                result += "\nAchievement unlocked: Air Crawler!"

            if self.player.current_room == self.server_room and not self.flags["scientist_met"]:
                self.flags["scientist_met"] = True
                result += (
                    "\n\nA woman looks up from the corner of the room.\n"
                    "She seems surprised but not hostile.\n"
                    "Type 'talk' to speak with her."
                )

            return result

        elif action == "look":

            room = self.player.current_room
            exits = ", ".join(room.connections.keys()) or "none"
            desc = room.description + f"\nExits: {exits}\n\nItems:\n" + room.list_items()

            if room == self.exit_room:
                desc += "\n\n" + self.exit_status()

            return desc

        elif action == "status":

            if self.player.current_room != self.exit_room:
                return "Nothing to check here."

            return self.exit_status()

        elif action == "items":
            return self.player.current_room.list_items()

        elif action == "take":

            if len(parts) < 2:
                return "Take what?"

            return self.player.take(parts[1])

        elif action == "inv":
            return self.player.show_inventory()

        elif action == "use":

            if len(parts) < 2:
                return "Use what?"

            return self.use_item(parts[1])

        elif action == "inspect":

            if len(parts) < 2:
                return "Inspect what?"

            return self.inspect_item(parts[1])

        elif action == "talk":

            room = self.player.current_room

            if room == self.hall:
                self.flags["met_guard"] = True
                return self.guard.talk()

            if room == self.server_room:
                return self.scientist.talk()

            return "There's no one here to talk to."

        elif action == "choose":

            if len(parts) < 2:
                return "Choose which option?"

            try:
                choice = int(parts[1])
                room = self.player.current_room

                if room == self.hall:
                    return self._guard_choose(choice)

                if room == self.server_room:
                    return self._scientist_choose(choice)

                return "No one to choose with."

            except ValueError:
                return "Invalid choice."

        elif action == "puzzle":

            room = self.player.current_room

            if room == self.exit_room:
                if not self.flags["exit_card_used"]:
                    return "The logic gate is dormant. Clear Lock 1 first."
                if not self.flags["exit_power_cut"]:
                    return "The logic gate is dormant. Clear Lock 2 first."
                return room.puzzle.question

            if room.puzzle:
                return room.puzzle.question

            return "No puzzle here."

        elif action == "solve":

            room = self.player.current_room

            if not room.puzzle:
                return "No puzzle here."

            if room == self.exit_room:
                if not self.flags["exit_card_used"]:
                    return "Clear Lock 1 first.\nHint: use your AccessCard."
                if not self.flags["exit_power_cut"]:
                    return "Clear Lock 2 first.\nHint: use Wire + Battery to cut power."

            answer = " ".join(parts[1:])
            result = room.puzzle.try_solve(answer, self.player)

            if room.puzzle.solved:

                self.achievements.unlock("Puzzle Solver")

                if room == self.lab:
                    self.flags["lab_unlocked"] = True

                if room == self.server_room:
                    self.flags["server_hacked"] = True
                    result += "\nAchievement unlocked: Ghost in the Machine!"
                    self.achievements.unlock("Ghost in the Machine")

                if room == self.exit_room:
                    result += (
                        "\n\nThe three lock indicators flip to GREEN one by one.\n"
                        "A low mechanical groan fills the room.\n"
                        "The massive steel door slides open.\n\n"
                        "Beyond it — darkness, then a sliver of pale light.\n"
                        "Outside air rushes in. Cold. Real.\n\n"
                        "You step forward."
                    )

            else:
                if room == self.exit_room:
                    self.failed_attempts += 1
                    remaining = 3 - self.failed_attempts
                    if remaining > 0:
                        result += f"\n\nWarning: security system has registered a failed attempt."
                        result += f"\n{remaining} attempt(s) remaining before lockdown."
                    else:
                        result += self._trigger_bad_ending()

            return result

        elif action == "achievements":
            return self.achievements.show()

        elif action == "save":
            SaveManager.save(self)
            return "Game saved."

        elif action == "load":
            data = SaveManager.load()
            return self.apply_load(data)

        elif action == "help":
            return self.help()

        elif action == "quit":
            self.running = False
            return "Goodbye."

        return f"Unknown command: '{action}'. Type 'help' for a list of commands."


    def _guard_choose(self, choice):

        result = self.guard.choose(choice)
        node = self.guard.dialogue_tree.get(self.guard.state, {})
        flag = node.get("flag")

        if flag == "trusted_guard":
            self.flags["trusted_guard"] = True
            self.achievements.unlock("Trusted")

        if flag == "found_truth":
            self.flags["found_truth"] = True
            self.achievements.unlock("Truth Seeker")
            result += "\nAchievement unlocked: Truth Seeker!"

        if flag == "guard_alarmed":
            self.flags["guard_alarmed"] = True
            result += self._trigger_bad_ending()

        return result

    def _scientist_choose(self, choice):

        result = self.scientist.choose(choice)
        node = self.scientist.dialogue_tree.get(self.scientist.state, {})
        flag = node.get("flag")

        if flag == "scientist_trusted":
            self.flags["scientist_trusted"] = True

        if flag == "found_truth":
            self.flags["found_truth"] = True
            self.achievements.unlock("Truth Seeker")
            result += "\nAchievement unlocked: Truth Seeker!"

        return result


    def _trigger_bad_ending(self):

        self.endings.set("bad")
        self.running = False

        if self.flags.get("guard_alarmed"):
            return (
                "\n\n╔══════════════════════════════════╗\n"
                "║     SECURITY LOCKDOWN ACTIVE     ║\n"
                "╚══════════════════════════════════╝\n\n"
                "Boots thunder down the corridor.\n"
                "Three guards round the corner at a sprint.\n\n"
                "You back against the wall. There's nowhere to go.\n\n"
                "Guard: *coldly* Take them back to the cell.\n"
                "       Increase the sedative dosage.\n\n"
                "The last thing you see is the ceiling lights\n"
                "blurring as they carry you away."
            )
        else:
            return (
                "\n\n╔══════════════════════════════════╗\n"
                "║     SECURITY LOCKDOWN ACTIVE     ║\n"
                "╚══════════════════════════════════╝\n\n"
                "The door panel SCREAMS an alert.\n"
                "Red lights strobe across the room.\n\n"
                "A synthesized voice announces:\n"
                "  'INTRUSION DETECTED. MAXIMUM SECURITY PROTOCOL ENGAGED.'\n\n"
                "Steel shutters slam down over every exit.\n"
                "The room pressurizes with a hiss.\n\n"
                "You sink to the floor.\n"
                "The facility has won."
            )


    def _consume(self, item_name):
        """Remove an item from the player's inventory by name."""
        self.player.inventory = [
            i for i in self.player.inventory
            if i.name.lower() != item_name.lower()
        ]

    def use_item(self, item_name):

        item_name_lower = item_name.lower()
        room = self.player.current_room

        item = next(
            (i for i in self.player.inventory if i.name.lower() == item_name_lower),
            None
        )

        if not item:
            return f"You don't have '{item_name}' in your inventory."

        if item.name == "JournalPage":
            return (
                "You unfold the torn page and read carefully:\n\n"
                "  '...moved to Sector 7B after the Level 3 incident.\n"
                "   New ID format they gave us: sector letters + level number.\n"
                "   Mine was 7B3. I hope nobody finds this.'\n\n"
                "The server room console asked for an employee ID...\n"
                "Sounds like the answer might be: 7b3"
            )

        if item.name == "Key":
            if room == self.cell:
                if self.flags["cell_unlocked"]:
                    return "The cell door is already open."
                self.flags["cell_unlocked"] = True
                self._consume("Key")
                return (
                    "You slide the rusty key into the lock.\n"
                    "It resists for a moment — then turns with a heavy CLUNK.\n\n"
                    "The cell door swings open.\n"
                    "You can now go east."
                )
            return "There's nothing here to use the Key on."

        if item.name == "Note":
            return (
                "You unfold the crumpled note and read:\n\n"
                "  'The first number: corners of a square.\n"
                "   The second number: wheels on a bicycle.\n"
                "   The third number: sides of a triangle.\n\n"
                "   — combine them and you have the code.'\n\n"
                "Think it through and use: solve <code>"
            )

        if item.name == "Wire":
            if self.player.has_item("Battery"):
                if room == self.lab:
                    return (
                        "You connect the Wire to the Battery and feed power\n"
                        "into the terminal's auxiliary port.\n"
                        "The screen flickers to life.\n"
                        "Try: solve echo"
                    )
                if room == self.exit_room:
                    return self._cut_exit_power()
                return "The Wire and Battery are ready — find something to power."
            return "The Wire needs a power source. Maybe that Battery would help."

        if item.name == "Battery":
            if self.player.has_item("Wire"):
                if room == self.lab:
                    return (
                        "You attach the Battery via the Wire to the terminal.\n"
                        "A faint hum fills the room.\n"
                        "Try: solve echo"
                    )
                if room == self.exit_room:
                    return self._cut_exit_power()
                return "Battery + Wire are ready. Find something that needs power."
            return "The Battery needs a conductor. The Wire might work."

        if item.name == "VentTool":
            if room == self.hall:
                self._consume("VentTool")
                return (
                    "You use the VentTool to unscrew the ventilation grate bolts.\n"
                    "The grate swings open with a metallic groan.\n"
                    "You can now go north."
                )
            return "You turn the screwdriver in your hand. Nothing to unscrew here."

        if item.name == "KeycardFragment":
            if self.player.has_item("AccessCard"):
                self._consume("KeycardFragment")
                return (
                    "You press the Fragment against the AccessCard's broken edge.\n"
                    "The chips align. The card crackles and glows faintly.\n"
                    "The AccessCard has been fully restored!\n"
                    "(The card reader at the Exit will accept it now.)"
                )
            return "The fragment is incomplete. You need the other half — an AccessCard."

        if item.name == "AccessCard":
            if room == self.exit_room:
                return self._swipe_exit_card()
            return "You wave the card around. Nothing responds to it here."

        if item.name == "DataChip":
            if room == self.lab:
                if self.flags.get("lab_unlocked"):
                    self.flags["found_truth"] = True
                    self.achievements.unlock("Truth Seeker")
                    self._consume("DataChip")
                    return (
                        "You insert the DataChip into the lab terminal.\n"
                        "Classified files begin to load...\n\n"
                        "SUBJECT: YOU\n"
                        "ROLE: Lead Researcher, Project ECHO\n"
                        "STATUS: Memory wiped. Re-inserted as test subject.\n\n"
                        "You were not a prisoner.\n"
                        "You built this place.\n"
                        "Achievement unlocked: Truth Seeker!"
                    )
                return (
                    "The terminal is offline. Activate it first.\n"
                    "Hint: use the Battery and Wire, then solve the lab puzzle."
                )
            return "You need a terminal to read this chip. The lab might have one."

        if item.hint:
            return f"You use the {item.name}.\nHint: {item.hint}"

        return item.inspect()

    def _swipe_exit_card(self):

        if self.flags["exit_card_used"]:
            return "Lock 1 is already disengaged. The card reader is dark."

        if not self.player.has_item("KeycardFragment"):
            return (
                "You swipe the AccessCard.\n"
                "The reader BEEPS — REJECTED.\n"
                "A display flashes: 'CARD INTEGRITY FAILURE. CHIP INCOMPLETE.'\n\n"
                "The card seems damaged. You need to repair it first.\n"
                "Hint: find the missing KeycardFragment."
            )

        self.flags["exit_card_used"] = True
        self._consume("AccessCard")
        return (
            "You press the restored card against the reader.\n"
            "A long pause... then a solid CLICK.\n\n"
            "  [LOCK 1] Card Reader — GREEN ✓\n\n"
            "One down. The magnetic seal on Lock 2 is still active.\n"
            "Hint: you'll need to cut power to the conduit."
        )

    def _cut_exit_power(self):

        if not self.flags["exit_card_used"]:
            return (
                "You approach the power conduit with the Wire and Battery.\n"
                "A warning light flashes: 'SEQUENCE ERROR — CARD AUTH REQUIRED FIRST.'\n"
                "Clear Lock 1 before tampering with the power system."
            )

        if self.flags["exit_power_cut"]:
            return "Lock 2 is already disengaged. The conduit is dead."

        self.flags["exit_power_cut"] = True
        self._consume("Wire")
        self._consume("Battery")
        return (
            "You locate the power conduit panel beside the door frame.\n"
            "With careful hands, you bridge the Wire between the Battery\n"
            "and the conduit's bypass terminal.\n\n"
            "A sharp CRACK. Sparks fly. The magnetic seal GROANS and releases.\n\n"
            "  [LOCK 2] Power Conduit — GREEN ✓\n\n"
            "The final panel flickers on — a logic gate challenge awaits.\n"
            "Type 'puzzle' to face Lock 3."
        )


    def inspect_item(self, item_name):

        item_name_lower = item_name.lower()

        item = next(
            (i for i in self.player.inventory if i.name.lower() == item_name_lower),
            None
        )

        if not item:
            item = next(
                (i for i in self.player.current_room.items if i.name.lower() == item_name_lower),
                None
            )

        if not item:
            return f"You don't see '{item_name}' here."

        return item.inspect()

    def check_endings(self):

        if not self.running:
            return

        if (
            self.player.current_room == self.exit_room
            and self.exit_room.puzzle
            and self.exit_room.puzzle.solved
        ):
            if self.flags["found_truth"]:
                self.endings.set("secret")
            else:
                self.endings.set("good")

            self.running = False


    def apply_load(self, data):

        if not data:
            return "No save data."

        room_name = data.get("current_room")
        if room_name not in self.rooms:
            return f"Save data references unknown room: {room_name}"
        self.player.current_room = self.rooms[room_name]

        self.player.inventory.clear()

        name_to_item = {}
        for room in self.rooms.values():
            for item in room.items:
                name_to_item[item.name] = item

        for item_name in data.get("inventory", []):
            if item_name in name_to_item:
                self.player.inventory.append(name_to_item[item_name])

        self.flags = data.get("flags", self.flags)
        self.achievements.unlocked = set(data.get("achievements", []))
        self.failed_attempts = data.get("failed_attempts", 0)

        return "Game loaded successfully."