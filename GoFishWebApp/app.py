from flask import Flask, render_template, session, flash
import cards
import random

app = Flask(__name__)
app.secret_key = "fdhghdfjghndfhgdlfgnh'odfahngldafhgjdafngjdfaghldkafngladkfngdfljka"

# Reset the game state
def reset_state():
    session["deck"] = cards.build_deck()

    session["computer"] = []  
    session["player"] = []
    session["player_pairs"] = []
    session["computer_pairs"] = []

    for _ in range(7):
        session["computer"].append(session["deck"].pop())
        session["player"].append(session["deck"].pop())
    session["player"], pairs = cards.identify_remove_pairs(session["player"])
    session["player_pairs"].extend(pairs)
    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    session["computer_pairs"].extend(pairs)

# Check if a player or computer has won
def check_winner():
    if len(session["player"]) == 0:
        flash("The Game is over. The player won! Great Job!")
        return True
    elif len(session["computer"]) == 0:
        flash("The Game is over. The computer won! Better look next time!")
        return True
    return False

# Route to the mainMenu
@app.get("/")
@app.get("/mainmenu")
def main_menu():
    return render_template(
        "mainmenu.html",
        title="Welcome to Go Fish!"
    )
# Route to start the game

@app.get("/startgame")
def start():
    reset_state()
    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]
    return render_template(
        "startgame.html",
        title="Let the games begin!",
        cards=card_images,
        n_computer=len(session["computer"]),
    )

# Process card selection
@app.get("/select/<value>")
def process_card_selection(value):
    found_it = False
    for n, card in enumerate(session["computer"]):
        if card.startswith(value):
            found_it = n
            break

    if isinstance(found_it, bool):
        flash("Go Fish!")
        
        # Check if the deck has cards before drawing
        if len(session["deck"]) > 0:
            session["player"].append(session["deck"].pop())
            flash(f"You drew a {session['player'][-1]}.")
        else:
            flash("The deck is empty! No more cards to draw.")

    else:
        flash(f"Here is your card from the computer: {session['computer'][n]}.")
        session["player"].append(session["computer"].pop(n))

    # Check for pairs and update player pairs
    session["player"], pairs = cards.identify_remove_pairs(session["player"])
    session["player_pairs"].extend(pairs)

    # Check if the game has ended
    if check_winner():
        card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]
        return render_template(
            "endgame.html",
            title="Game Over!",
            cards=card_images,
            n_computer=len(session["computer"]),
        )

    # Computer's turn
    if len(session["computer"]) > 0:
        card = random.choice(session["computer"])
        the_value = card[: card.find(" ")]
    else:
        the_value = ""

    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]
    return render_template(
        "pickcard.html",
        title="The computer wants to know",
        value=the_value,
        cards=card_images,
    )

# Process picked card from computer
@app.get("/pick/<value>")
def process_the_picked_card(value):
    if value == "0":
        # Check if the deck has cards before drawing
        if len(session["deck"]) > 0:
            session["computer"].append(session["deck"].pop())
        else:
            flash("The deck is empty! No more cards to draw.")
    else:
        for n, card in enumerate(session["player"]):
            if card.startswith(value.title()):
                break
        #flash(f"DEBUG: The picked card was at location {n}.")
        session["computer"].append(session["player"].pop(n))

    # Check for pairs and update computer pairs
    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    session["computer_pairs"].extend(pairs)

    # Check if the game has ended
    if check_winner():
        card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]
        return render_template(
            "endgame.html",
            title="Game Over!",
            cards=card_images,
            n_computer=len(session["computer"]),
        )

    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]
    return render_template(
        "startgame.html",
        title="Keep playing!",
        cards=card_images,
        n_computer=len(session["computer"]),
    )

if __name__ == "__main__":
    app.run(debug=True)
