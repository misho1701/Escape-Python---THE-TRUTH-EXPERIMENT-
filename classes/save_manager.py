import json


class SaveManager:

    @staticmethod
    def save(game):

        data = {
            "current_room": game.player.current_room.name,

            "inventory": [
                item.name for item in game.player.inventory
            ],

            "flags": game.flags,

            "achievements": list(game.achievements.unlocked),

            "failed_attempts": game.failed_attempts
        }

        with open("save.json", "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load():

        try:
            with open("save.json", "r") as f:
                return json.load(f)

        except FileNotFoundError:
            return None