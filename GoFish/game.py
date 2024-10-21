import asyncio
import cards
import random
from textual.app import App,ComposeResult
from textual.containers import Center
from textual.widgets import Static, Input, Button, Footer, Header

class GoFishApp(App):
    CSS_PATH = "go_fish.tcss"  # path to css file

    def __init__(self):  # initializes the game
        super().__init__() # calls the parent initaliser 
        self.initialize_game() # sets up the game variables and starts a new game

    def initialize_game(self):
        # Set up game variables
        self.deck = cards.build_deck()
        self.computer = []
        self.player = []
        self.player_pairs = []
        self.computer_pairs = []
        self.asking_for_card = False
        self.card_value = ""
        self.gameOver = False
        
        # Deal 7 cards to each player at the start of the game
        for _ in range(7):
            self.computer.append(self.deck.pop())
            self.player.append(self.deck.pop())

        # Remove pairs for computer and player
        self.player, pairs = cards.identify_remove_pairs(self.player)
        self.player_pairs.extend(pairs)
        self.computer, pairs = cards.identify_remove_pairs(self.computer)
        self.computer_pairs.extend(pairs)
     # Defines the layout for UI
    def compose(self)-> ComposeResult:
        yield Header()
        yield Static("Welcome to Go Fish!", id="main_text")
        yield Static("Player's Hand:", id="player_hand__identity_text")
        yield Static("Player's Hand:", id="player_hand")
        with Center():
         yield Input(placeholder="Enter a number to select a card", id="input_box")
        with Center(): # just so the buttons are centered on screen
         yield Button("Play Turn", id="play_turn_button")
        with Center():
         yield Button("Play Again?", id="play_again_button")  
        yield Footer()
    
    # this displays the current hand of they player, with the pairs removed 
    def show_player_hand(self):
        player_hand_text = "\n".join([f"Select {n} for {card}" for n, card in enumerate(self.player)])
        self.query_one("#player_hand").update(player_hand_text)
    
    # Called when the textual is launched, setting up the initial state
    async def on_mount(self):
        await self.update_display("Welcome to Go Fish!") # opening message that displays to player
        self.show_player_hand()

    # For updating the text onscreen during gameplay
    async def update_display(self, text):
        self.query_one("#main_text").update(text)
        
    # For button clicks for "Play Turn" and "Play Again" buttons
    async def on_button_pressed(self, event):
        if event.button.id == "play_turn_button": # this checks if the player has clicked on the play turn button
            choice_text = self.query_one("#input_box").value.strip()
            if self.asking_for_card:
                if choice_text.lower() in ["y", "n", "yes", "no"]: # which inputs are allowed 
                    await self.handle_player_response(choice_text.lower())
                else:
                    await self.update_display("Please enter 'y' or 'n'.") # error check to the right input
                self.query_one("#input_box").value = ""  # clears the text box
            else:
                if choice_text.isdigit() and 0 <= int(choice_text) < len(self.player):
                    await self.play_game(int(choice_text))
                else:
                    await self.update_display("Please enter a valid card number.") # error check if the wrong number is entered
                    self.query_one("#input_box").value = ""
        elif event.button.id == "play_again_button": # if play again button is pressed it resets the game
            self.gameOver = True
            await self.reset_game()
            
    # Resets game state and starts a new game for replay
    async def reset_game(self):
        self.initialize_game()  
        await self.update_display("Starting a new game. Good luck!") # positive message because sure why not?
        await asyncio.sleep(1.0)
        self.show_player_hand()
        await self.update_display("Welcome to Go Fish!")
        self.gameOver = False

     # Handle player's response to the computer's requests
    async def handle_player_response(self, response):
        if response in ["y", "yes"]: #  if Player has the requested card
            for n, card in enumerate(self.player): # helps to interate through loop and keep track of values avoids a counter
                if card.startswith(self.card_value): # Finds a matching card
                    self.computer.append(self.player.pop(n)) # gives the card to the enemy :O
                    self.show_player_hand()  # Ensure display updates immediately
                    await self.update_display(f"The computer took your {self.card_value}.")
                    await asyncio.sleep(1.0)
                    break
        elif response in ["n", "no"]: # if player doesnt have the requested card
            self.computer.append(self.deck.pop())
            self.show_player_hand()  # Immediate update after modifying computer's hand
            await self.update_display("The computer drew a card from the deck.")
            await asyncio.sleep(1.0)
            if len(self.deck) == 0:
                await self.update_display("The deck is empty. Game Over.")
                self.gameOver = True
                return

        self.asking_for_card = False # Ends the response phase
        await self.update_game_state() # continues the game
      # Handle player's turn and card selection
    async def play_game(self, choice):
        self.player.sort()
        selection = self.player[choice] 
        self.card_value = selection.split(" ")[0]  # Get card value prefix and drops the type
        # Checks if computer has a card matching player's choice
        found_it = next((n for n, card in enumerate(self.computer) if card.startswith(self.card_value)), None)

        if found_it is None: # Computer doesn't have matching card
            await self.update_display("\nGo Fish!\n")
            await asyncio.sleep(1.0)
            self.player.append(self.deck.pop())
            self.show_player_hand() # immediately updates the player hand on screen
            await self.update_display(f"You drew a {self.player[-1]}.")
            await asyncio.sleep(1.0) # delay so the text can be seen by the player
            if len(self.deck) == 0:
                await self.update_display("The deck is empty. Game Over.")
                return
        else:
            # Computer gives matching card to player
            await self.update_display(f"Here is your card from the computer: {self.computer[found_it]}.")
            self.player.append(self.computer.pop(found_it))
            self.show_player_hand()  # immediately updates the player hand on screen
            await asyncio.sleep(1.0)

        self.player, pairs = cards.identify_remove_pairs(self.player)
        self.player_pairs.extend(pairs)
        self.show_player_hand()  # Update after removing pairs
        
        # Check win conditions
        if len(self.player) == 0:
            await self.update_display("The Game is over. The player won.")
            self.gameOver = True
            return
        if len(self.computer) == 0:
            await self.update_display("The Game is over. The computer won.")
            self.gameOver = True
            return

        self.asking_for_card = True
        await self.update_display(f"The computer asks: Do you have a {self.card_value}? (y/n)")
    # Update game state at the end of each turn
    async def update_game_state(self):
        self.computer, pairs = cards.identify_remove_pairs(self.computer)
        self.computer_pairs.extend(pairs)
        self.show_player_hand()  # Immediate update after modifying computer's hand
        await asyncio.sleep(1.0)
        await self.update_display("Player turn: select a card from the list")
        
        # Check win conditions
        if len(self.computer) == 0:
            await self.update_display("The Game is over. The computer won.")
            self.gameOver = True
        elif len(self.player) == 0:
            await self.update_display("The Game is over. The player won.")
            self.gameOver = True
 # runs the app
if __name__ == "__main__":
    game = GoFishApp()
    game.run()