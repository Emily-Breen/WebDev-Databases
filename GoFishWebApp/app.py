from flask import Flask, render_template, session, flash, request, redirect, url_for
import cards
import random
import cards
import random
from DBcm import UseDatabase

app = Flask(__name__)
app.secret_key = "fdhghdfjghndfhgdlfgnh'odfahngldafhgjdafngjdfaghldkafngladkfngdfljka"


creds = {
    "host": "localhost",
    "port": 3306,
    "user": "gofishuser",
    "password": "gofishpasswd",
    "database": "gofishDB",
    
}
app.config["creds"] = creds
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

# Store the game result in the leaderboard
def store_game_result(winner):
    score = len(session["player_pairs"]) if winner == "Player" else len(session["computer_pairs"])
    with UseDatabase(creds) as cursor:
        cursor.execute("""
            INSERT INTO leaderboard (player_id, score, result)
            VALUES (%s, %s, %s)
        """, (session["player_id"], score, winner))
# Register route to get player handle


# Route to the mainMenu
# Route for main menu with registration form
@app.route("/", methods=["GET", "POST"])
@app.route("/mainmenu", methods=["GET", "POST"])
def main_menu():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            with UseDatabase(creds) as cursor:
                _SQL = "SELECT id FROM Players WHERE handle=%s"
                cursor.execute(_SQL, (username,))
                result = cursor.fetchone()
                if not result:
                    # New user, insert into Players
                    _SQL = "INSERT INTO Players (handle) VALUES (%s)"
                    cursor.execute(_SQL, (username,))
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    result = cursor.fetchone()
                session["player_id"] = result[0]
                flash(f"Welcome, {username}!")
                return redirect(url_for("start"))
        else:
            flash("Please enter a username.")
    
    return render_template("mainmenu.html", title="Welcome to Go Fish!")
# Route to start the game

@app.route("/startgame", methods=["GET"])
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
@app.route("/select/<value>", methods=["GET"])

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
