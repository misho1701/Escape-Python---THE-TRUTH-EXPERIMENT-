from game import Game


def show_menu():

    while True:

        print("""
==================================
        ESCAPE PYTHON
    THE TRUTH EXPERIMENT
==================================

1. New Game
2. Help
3. Exit
""")

        choice = input("Choice: ")

        if choice == "1":
            return True

        elif choice == "2":

            print("""
Escape the underground facility.

Collect items.
Solve puzzles.
Talk to NPCs.
Discover the truth.
""")

        elif choice == "3":
            return False


def main():

    if not show_menu():
        return

    game = Game()

    print("""
You slowly regain consciousness.

Your head hurts.

You don't remember who you are.

You don't remember how you got here.

A cold prison cell surrounds you.

Maybe there is a way out...
""")

    input("\nPress ENTER to continue...")

    while game.running:

        print(
            f"\nLocation: "
            f"{game.player.current_room.name}"
        )

        command = input("> ")

        result = game.process(command)

        if result:
            print(result)

        game.check_endings()

    print("\n===== ENDING =====")
    print(game.endings.show())


if __name__ == "__main__":
    main()