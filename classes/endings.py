class Endings:

    def __init__(self):
        self.current = None

    def set(self, ending):
        self.current = ending

    def show(self):

        endings = {

            "good": """
╔══════════════════════════════════════╗
║             GOOD ENDING              ║
╚══════════════════════════════════════╝

The door opens.

Cold air rushes in — real air, moving air,
air that hasn't been recycled a thousand times.

You step out into darkness and then, slowly,
a grey pre-dawn sky comes into focus above you.

You don't know your name.
You don't know who you were.

But you're free.

For now, that's enough.
""",

            "bad": """
╔══════════════════════════════════════╗
║              BAD ENDING              ║
╚══════════════════════════════════════╝

The facility wins.

You are returned to your cell.
The sedative is stronger this time.

When you wake again, you won't remember
the corridor, the servers, or the door
that almost opened.

You won't remember trying.

The experiment continues.
""",

            "secret": """
╔══════════════════════════════════════╗
║            SECRET ENDING             ║
╚══════════════════════════════════════╝

The door opens.

You walk out into the cold morning air
and stop.

You remember now.

The blueprints you drew.
The consent forms you signed — and then stopped signing.
The moment you decided to go first,
to prove it was safe.

It wasn't safe.

You built this place.
You ran the experiment.
You were the experiment.

Project ECHO is over.

Somewhere behind you, in the dark,
Dr. Voss is still waiting.

You turn around.
"""
        }

        return endings.get(
            self.current,
            "No ending reached."
        )