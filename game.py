import cards
import random
from textual.app import App


class GoFishApp(App): 
    def __init__(self):
        super().__init__()
        self.deck = cards.build_deck()
        self.computer = []
        self.player = []
        self.player_pairs = []
        self.computer_pairs = []

       
        for _ in range(7):
            self.computer.append(self.deck.pop())
            self.player.append(self.deck.pop())

       
        self.player, pairs = cards.identify_remove_pairs(self.player)
        self.player_pairs.extend(pairs)
        self.computer, pairs = cards.identify_remove_pairs(self.computer)
        self.computer_pairs.extend(pairs)

    def show_player_hand(self):
        print("\nPlayers hand:")
        for n, card in enumerate(self.player):
            print(f"\tSelect {n} for {card}")

    def play_game(self):
        while True:
            self.player.sort()

            self.show_player_hand()
            choice = input(
                "\nPlease select the number for the card you want from the above list"
            )
            choice = int(choice)
            selection = self.player[int(choice)]
            value = selection[: selection.find(" ")]

            found_it = False
            for n, card in enumerate(self.computer):
                if card.startswith(value):
                    found_it = n
                    break

            if isinstance(found_it, bool):
                print("\nGo Fish!\n")
                self.player.append(self.deck.pop())
                print(f"You drew a {self.player[-1]}.")
                if len(self.deck) == 0:
                    break
            else:
                print(f"Here is your card from the computer: {self.computer[n]}.")
                self.player.append(self.computer.pop(n))

            self.player, pairs = cards.identify_remove_pairs(self.player)
            self.player_pairs.extend(pairs)
            self.show_player_hand()

            if len(self.player) == 0:
                print("The Game is over. The player won.")
                break
            if len(self.computer) == 0:
                print("The Game is over. The computer won.")
                break

            card = random.choice(self.computer)
            value = card[: card.find(" ")]

            choice = input(f"\nFrom the computer: Do you have a {value}? (y/n) ")

            if choice in ["y", "Y", "yes", "YES", "Yes"]:
                for n, card in enumerate(self.player):
                    if card.startswith(value):
                        break
                self.computer.append(self.player.pop(n))
            else:
                self.computer.append(self.deck.pop())
                if len(self.deck) == 0:
                    break

            self.computer, pairs = cards.identify_remove_pairs(self.computer)
            self.computer_pairs.extend(pairs)

            if len(self.computer) == 0:
                print("The Game is over. The computer won.")
                break
            if len(self.player) == 0:
                print("The Game is over. The player won.")
                break

        if len(self.deck) == 0:
            print("Game over.")
            if len(self.player_pairs) == len(self.computer_pairs):
                print("It's a draw.")
            elif len(self.player_pairs) > len(self.computer_pairs):
                print("The Game is over. The player won.")
            else:
                print("The Game is over. The computer won.")

# To run the game:
if __name__ == "__main__":
    game = GoFishApp()
    game.run()