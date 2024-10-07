import asyncio  # had to use this as the text was updating too quickly for the player to see and looked broken
import cards
import random
from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Button, Footer, Header

class GoFishApp(App):
    CSS_PATH = "go_fish.tcss" # path to css file

    def __init__(self): # initalizes the game
        super().__init__()
        self.deck = cards.build_deck()
        self.computer = []
        self.player = []
        self.player_pairs = []
        self.computer_pairs = []
        self.asking_for_card = False
        self.card_value = ""

        # Initialize hands for player and computer
        for _ in range(7):
            self.computer.append(self.deck.pop())
            self.player.append(self.deck.pop())

        # Remove initial pairs
        self.player, pairs = cards.identify_remove_pairs(self.player)
        self.player_pairs.extend(pairs)
        self.computer, pairs = cards.identify_remove_pairs(self.computer)
        self.computer_pairs.extend(pairs)

    def compose(self) -> ComposeResult: #creates 
        yield Header()
        yield Static("Welcome to Go Fish!", id="main_text")
        yield Static("Player's Hand:", id="player_hand")
        yield Input(id="input_box")
        yield Button("Play Turn", id="play_turn_button")
        yield Footer()

    def show_player_hand(self):
        player_hand_text = "\n".join([f"Select {n} for {card}" for n, card in enumerate(self.player)])
        self.query_one("#player_hand").update(player_hand_text)

    async def on_mount(self):
        await self.update_display("Welcome to Go Fish!")
        self.show_player_hand()

    async def update_display(self, text):
        self.query_one("#main_text").update(text)
        print(f"Updated display with: {text}") 

    async def on_button_pressed(self, event):
        if event.button.id == "play_turn_button":
            choice_text = self.query_one("#input_box").value.strip()
            if self.asking_for_card:
                
                if choice_text in ["y", "n", "Y", "N"]:
                    await self.handle_player_response(choice_text)
                else:
                    await self.update_display("Please enter 'y' or 'n'.")
                self.query_one("#input_box").value = ""  # clears the text box 
            else:
                # Handle player's turn selection
                if choice_text.isdigit() and 0 <= int(choice_text) < len(self.player):
                    await self.play_game(int(choice_text))
                else:
                    await self.update_display("Please enter a valid card number.")
                    self.query_one("#input_box").value = "" # clears the text box 

    async def handle_player_response(self, response):
        if response == "y":
            for n, card in enumerate(self.player):
                if card.startswith(self.card_value):
                    self.computer.append(self.player.pop(n))
                    await self.update_display(f"The computer took your {self.card_value}.")
                    break
        else:  
            self.computer.append(self.deck.pop())
            await self.update_display("The computer drew a card from the deck.")
            await asyncio.sleep(1.0) #slows so you can see the updates
            if len(self.deck) == 0:
                await self.update_display("The deck is empty. Game Over.")
                return

        self.asking_for_card = False  
        await self.update_game_state()

    async def play_game(self, choice):
        self.player.sort()
        selection = self.player[choice]
        self.card_value = selection[: selection.find(" ")]

        found_it = False
        for n, card in enumerate(self.computer):
            if card.startswith(self.card_value):
                found_it = n
                break

        if isinstance(found_it, bool):
            await self.update_display("\nGo Fish!\n")
            await asyncio.sleep(1.0)  #slows so you can see the updates
            self.player.append(self.deck.pop())
            await self.update_display(f"You drew a {self.player[-1]}.")
            await asyncio.sleep(1.0)
            if len(self.deck) == 0:
                await self.update_display("The deck is empty. Game Over.")
                return
        else:
            await self.update_display(f"Here is your card from the computer: {self.computer[n]}.")
            self.player.append(self.computer.pop(n))
            await asyncio.sleep(1.0)

        self.player, pairs = cards.identify_remove_pairs(self.player)
        self.player_pairs.extend(pairs)
        self.show_player_hand()

        if len(self.player) == 0:
            await self.update_display("The Game is over. The player won.")
            return
        if len(self.computer) == 0:
            await self.update_display("The Game is over. The computer won.")
            return

        # Computer asks if the player has a certain value
        self.asking_for_card = True  
        await self.update_display(f"The computer asks: Do you have a {self.card_value}? (y/n)")
        

    async def update_game_state(self):
        self.computer, pairs = cards.identify_remove_pairs(self.computer)
        self.computer_pairs.extend(pairs)

        if len(self.computer) == 0:
            await self.update_display("The Game is over. The computer won.")
        elif len(self.player) == 0:
            await self.update_display("The Game is over. The player won.")

if __name__ == "__main__":
    game = GoFishApp()
    game.run()