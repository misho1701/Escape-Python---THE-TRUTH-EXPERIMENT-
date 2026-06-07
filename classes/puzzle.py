class Puzzle:

    def __init__(self, question, answer, reward="", required_item=None):

        self.question = question
        self.answer = answer.lower()
        self.reward = reward
        self.required_item = required_item
        self.solved = False

    def try_solve(self, user_answer, player=None):

        if self.solved:
            return "Already solved."

        if self.required_item and player:

            has_item = any(
                i.name.lower() == self.required_item.lower()
                for i in player.inventory
            )

            if not has_item:
                return f"You need {self.required_item} to solve this."

        if user_answer.lower() == self.answer:

            self.solved = True

            return f"Correct! {self.reward}"

        return "Wrong answer."