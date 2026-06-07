class Achievements:

    def __init__(self):
        self.unlocked = set()

    def unlock(self, achievement):

        self.unlocked.add(achievement)

    def show(self):

        if not self.unlocked:
            return "No achievements unlocked."

        return "\n".join(
            f"- {achievement}"
            for achievement in self.unlocked
        )