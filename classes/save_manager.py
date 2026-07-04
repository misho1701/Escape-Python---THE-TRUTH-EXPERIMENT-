import json
import os
import shutil
from datetime import datetime


SAVE_DIR  = "saves"
MAX_SLOTS = 3


class SaveManager:

    @staticmethod
    def _ensure_dir():
        os.makedirs(SAVE_DIR, exist_ok=True)

    @staticmethod
    def _path(slot):
        return os.path.join(SAVE_DIR, f"save_slot_{slot}.json")

    @staticmethod
    def _backup(slot):
        path = SaveManager._path(slot)
        if os.path.exists(path):
            shutil.copy2(path, path + ".bak")

    @staticmethod
    def _solved_puzzles(game):
        solved = []
        for name, room in game.rooms.items():
            if room.puzzle and room.puzzle.solved:
                solved.append(name)
        return solved

    @staticmethod
    def save(game, slot=1):
        if slot not in range(1, MAX_SLOTS + 1):
            return f"Invalid slot. Choose 1–{MAX_SLOTS}."

        SaveManager._ensure_dir()
        SaveManager._backup(slot)

        data = {
            "slot":         slot,
            "saved_at":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_room": game.player.current_room.name,
            "inventory":    [item.name for item in game.player.inventory],
            "flags":        game.flags,
            "achievements": list(game.achievements.unlocked),
            "failed_attempts": game.failed_attempts,
            "solved_puzzles":  SaveManager._solved_puzzles(game),
        }

        path = SaveManager._path(slot)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return f"Game saved to slot {slot}."
        except OSError as e:
            return f"Save failed: {e}"

    @staticmethod
    def load(slot=1):
        if slot not in range(1, MAX_SLOTS + 1):
            return None, f"Invalid slot. Choose 1–{MAX_SLOTS}."

        path = SaveManager._path(slot)

        if not os.path.exists(path):
            return None, f"No save found in slot {slot}."

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            required = {"current_room", "inventory", "flags", "achievements"}
            missing  = required - data.keys()
            if missing:
                return None, f"Save file is incomplete (missing: {', '.join(missing)})."

            return data, None

        except json.JSONDecodeError:
            bak = path + ".bak"
            if os.path.exists(bak):
                try:
                    with open(bak, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return data, "Save file was corrupted — loaded from backup."
                except json.JSONDecodeError:
                    pass
            return None, "Save file is corrupted and backup also failed."

        except OSError as e:
            return None, f"Load failed: {e}"

    @staticmethod
    def list_saves():
        SaveManager._ensure_dir()
        lines = []
        for slot in range(1, MAX_SLOTS + 1):
            path = SaveManager._path(slot)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    saved_at = data.get("saved_at", "unknown")
                    room     = data.get("current_room", "?")
                    inv      = len(data.get("inventory", []))
                    ach      = len(data.get("achievements", []))
                    lines.append(
                        f"  Slot {slot}: {saved_at}  |  Room: {room}"
                        f"  |  Items: {inv}  |  Achievements: {ach}"
                    )
                except (json.JSONDecodeError, OSError):
                    lines.append(f"  Slot {slot}: [corrupted]")
            else:
                lines.append(f"  Slot {slot}: empty")

        header = "=" * 44 + "\n  SAVE SLOTS\n" + "=" * 44
        return header + "\n" + "\n".join(lines) + "\n" + "=" * 44

    @staticmethod
    def delete(slot):
        if slot not in range(1, MAX_SLOTS + 1):
            return f"Invalid slot. Choose 1–{MAX_SLOTS}."

        path = SaveManager._path(slot)
        if not os.path.exists(path):
            return f"Slot {slot} is already empty."

        os.remove(path)
        bak = path + ".bak"
        if os.path.exists(bak):
            os.remove(bak)
        return f"Slot {slot} deleted."