# Escape Python: The Truth Experiment

A text adventure game built in Python. You wake up in a prison cell with no memory of who you are or how you got there. Your only goal: escape. But the deeper you go, the more you realise the facility has a darker secret — and so do you.

---

## Features

- 6 interconnected rooms to explore
- 9 unique items with context-aware `use` logic
- 5 puzzles of different types (riddles, authentication, logic gates)
- 2 NPCs with deep branching dialogue trees
- 3 endings — good, bad, and secret
- 5 unlockable achievements
- Full GUI via pygame with a live map, inventory panel, and scrollable output
- Save/load system via JSON

---

## Project Structure

```
escape_python/
│
├── main.py          — Terminal entry point. Menu, game loop, ending display.
├── gui.py           — Tkinter GUI. Full game window with live map and panels.
├── game.py          — Core engine. World creation, command processing, story logic.
│
├── room.py          — Room class. Holds description, connections, items, puzzle.
├── player.py        — Player class. Movement, inventory, item pickup.
├── item.py          — Item class. Name, description, type, usability, hints.
├── puzzle.py        — Puzzle class. Question, answer, reward, required item check.
├── npc.py           — NPC class. Branching dialogue tree, state machine.
│
├── achievements.py  — Achievement tracker. Unlock and display.
├── endings.py       — Ending definitions and display text.
├── save_manager.py  — Save/load via JSON. Persists room, inventory, flags, achievements.
├── story_flags.py   — Standalone flag utility (also managed inline in Game).
│
└── tests.py         — Unit tests for movement, item pickup, inventory.
```

---

## Running the Game

**GUI (recommended):**
```bash
python gui.py
```

**Terminal:**
```bash
python main.py
```

Requires Python 3.8 or higher. No external dependencies — Tkinter is built into Python.

---

## World Map

```
                    [Ventilation Shaft]
                           |
                          N/S
                           |
[Cell] --(E/W)-- [Hall] --(E/W)-- [Laboratory] --(E/W)-- [Exit]
                           |              ^
                          down            |
                           |             E
                    [Server Room] --------+
```

---

## Rooms

| Room | Description | NPC | Puzzle |
|---|---|---|---|
| **Cell** | Starting room. Cold, damp. Door is locked. | — | Number riddle — decode clues from the Note |
| **Hall** | Flickering corridor. Vent grate on the north wall. | Guard | None |
| **Ventilation Shaft** | Cramped ducts above the Hall. A torn page hidden inside. | — | Clock riddle — position at midnight |
| **Server Room** | Blue-lit server racks. A trapped researcher sits in the corner. | Dr. Voss | Employee ID authentication |
| **Laboratory** | Broken monitors, active terminal. Story revelation here. | — | Terminal activation — power it up |
| **Exit** | Three-lock door. Point of no return. Alarm triggers on entry. | — | Sequential three-lock challenge |

---

## NPCs

### Guard — Hall

A night-shift guard who's been having doubts about the facility for years. Has 14 dialogue nodes across multiple branches. How you approach him determines whether he helps you or triggers a lockdown.

- Build trust → he reveals the exit passphrase and vent route
- Stay silent → he slips you information unprompted
- Threaten him → he reaches for the alarm panel. One chance to stop him.
- Push too far → **bad ending**

### Dr. Voss — Server Room

A junior researcher who has been trapped in the server room since the facility lockdown six months ago. Has 12 dialogue nodes. She knows more about Project ECHO — and about you — than she initially lets on.

- Ask about the project → she explains the memory wipe procedure
- Ask about the researcher → she starts to reveal the truth
- Ask who you are → she tells you to find the DataChip
- Confirm your identity with her → unlocks `found_truth` and the secret ending path

---

## Items

| Item | Found In | Purpose |
|---|---|---|
| **Key** | Cell | Unlocks the cell door — must `use Key` to leave |
| **Note** | Cell | Shows the encoded number riddle for the cell puzzle |
| **VentTool** | Cell | Unscrews the vent grate in the Hall — required to go north |
| **Wire** | Hall | Combined with Battery to power electronics or cut the exit conduit |
| **JournalPage** | Ventilation Shaft | Reveals the server room employee ID through narrative |
| **KeycardFragment** | Server Room | Repairs the AccessCard — required for Exit Lock 1 |
| **DataChip** | Server Room | Insert into the lab terminal to decrypt classified files and reveal the truth |
| **Battery** | Laboratory | Powers the lab terminal; combined with Wire for the exit |
| **AccessCard** | Laboratory | Swipe at Exit Lock 1 — must be repaired with the Fragment first |

---

## Puzzles

| Room | Type | Answer |
|---|---|---|
| Cell | Decode riddles from the Note | `423` |
| Ventilation Shaft | Clock position riddle | `center` |
| Server Room | ID format: sector letters + level | `7b3` |
| Laboratory | Terminal activation passphrase | `echo` |
| Exit — Lock 3 | Logic riddle: no mouth, no ears, alive with wind | `echo` |

---

## Exit Door — Three Locks

The final door requires three steps cleared in order:

1. **Lock 1 — Card Reader** — `use AccessCard` (requires KeycardFragment in inventory to repair it first)
2. **Lock 2 — Power Conduit** — `use Wire` or `use Battery` (requires both; shorts the magnetic seal)
3. **Lock 3 — Logic Gate** — `puzzle` then `solve <answer>` (only unlocks after locks 1 and 2)

Type `status` inside the Exit room to check progress at any time.

---

## Endings

| Ending | How to reach |
|---|---|
| **Good** | Clear all three exit locks and escape without learning the truth |
| **Secret** | Escape after discovering the truth — via the DataChip, the Guard, or Dr. Voss |
| **Bad** | Trigger the Guard's alarm, or fail the exit puzzle 3 times |

---

## Achievements

| Achievement | How to unlock |
|---|---|
| **Puzzle Solver** | Solve any puzzle |
| **Air Crawler** | Enter the Ventilation Shaft for the first time |
| **Ghost in the Machine** | Hack the server room console |
| **Truth Seeker** | Discover the truth about Project ECHO |
| **Trusted** | Earn the Guard's trust through dialogue |

---

## Commands

```
go <direction>      Move between rooms  (east, west, north, south, up, down)
look                Describe the current room and list exits
items               List items visible in the room
take <item>         Pick up an item
inv                 Show your inventory
use <item>          Use an item  (effects depend on location and context)
inspect <item>      Read detailed description and hint for an item
talk                Start dialogue with an NPC in the room
choose <number>     Pick a dialogue option
puzzle              Show the current room's puzzle
solve <answer>      Attempt to solve the puzzle
status              Show exit door lock progress  (Exit room only)
save / load         Save or load the game  (saves to save.json)
achievements        Show unlocked achievements
help                Show command list
quit                Exit the game
```

---

## Save System

Progress is saved to `save.json` in the project root. The following state is persisted:

- Current room
- Inventory contents
- All story flags
- Unlocked achievements
- Failed puzzle attempt count

---

## Running Tests

```bash
python tests.py
```

Covers room connections, item pickup, and inventory display.
