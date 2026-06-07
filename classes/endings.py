class Endings:

    def __init__(self):
        self.current = None

    def set(self, ending):

        self.current = ending

    def show(self):

        endings = {

            "good":
            """
GOOD ENDING

You escaped the facility.

The sun shines in your eyes as you leave
the underground complex behind forever.
""",

            "bad":
            """
BAD ENDING

Security systems activate.

The facility enters lockdown.

You never escape.
""",

            "secret":
            """
SECRET ENDING

The terminal reveals the truth.

You were one of the scientists.

This facility exists because of you.
"""
        }

        return endings.get(
            self.current,
            "No ending reached."
        )