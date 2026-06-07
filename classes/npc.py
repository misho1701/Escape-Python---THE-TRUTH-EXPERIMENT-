class NPC:

    def __init__(self, name, dialogue_tree):

        self.name = name
        self.dialogue_tree = dialogue_tree
        self.state = "start"

    def talk(self):

        node = self.dialogue_tree[self.state]

        text = node["text"]

        if "options" not in node:
            return text

        result = text + "\n\n"

        for i, option in enumerate(node["options"], start=1):

            result += f"{i}. {option['text']}\n"

        return result

    def choose(self, choice):

        node = self.dialogue_tree[self.state]

        if "options" not in node:
            return "No choices available."

        try:

            option = node["options"][choice - 1]

        except IndexError:

            return "Invalid choice."

        self.state = option["next"]

        return option.get("result", "Choice made.")