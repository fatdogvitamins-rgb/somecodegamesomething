import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit

from arena import DodgeArena
from storage import AccountStore

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY", "dev-secret")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
store = AccountStore(os.environ.get("APP_DB_PATH", "players.db"))
arena = DodgeArena(width=480, height=320, reward_coins=25)
store.initialize()


@app.route("/")
def home():
    username = session.get("username")
    profile = store.get_user(username) if username else None
    leaderboard = store.get_leaderboard()
    return render_template("home.html", profile=profile, leaderboard=leaderboard, error=None)


@app.post("/signup")
def signup():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not username or len(password) < 6:
        leaderboard = store.get_leaderboard()
        return (
            render_template(
                "home.html",
                profile=None,
                leaderboard=leaderboard,
                error="Pick a name and a longer password.",
            ),
            400,
        )
    if not store.create_user(username, password):
        leaderboard = store.get_leaderboard()
        return (
            render_template(
                "home.html",
                profile=None,
                leaderboard=leaderboard,
                error="That username is already taken.",
            ),
            400,
        )
    session["username"] = username
    return redirect(url_for("home"))


@app.post("/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not store.verify_user(username, password):
        leaderboard = store.get_leaderboard()
        return (
            render_template(
                "home.html",
                profile=None,
                leaderboard=leaderboard,
                error="Wrong username or password.",
            ),
            400,
        )
    session["username"] = username
    return redirect(url_for("home"))


@app.route("/lobby")
def lobby_page():
    if "username" not in session:
        return redirect(url_for("home"))
    return render_template("lobby.html", username=session["username"])


@app.route("/game")
def game_page():
    if "username" not in session:
        return redirect(url_for("home"))
    return render_template("game.html", username=session["username"])


@app.route("/score", methods=["POST"])
def receive_score():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    score = data.get("score")

    if not isinstance(name, str) or not isinstance(score, int):
        return jsonify({"error": "Send a player name and a whole-number score."}), 400

    return jsonify({"message": "Score received!", "name": name, "score": score})


@socketio.on("join_game")
def handle_join_game(data):
    username = session.get("username")
    if not username:
        return
    arena.add_player(username)
    if len(arena.players) >= 2 and not arena.round_active:
        arena.start_round()
    emit(
        "state_update",
        {"players": arena.players, "hazards": arena.hazards, "round_active": arena.round_active},
        broadcast=True,
    )


@socketio.on("move")
def handle_move(data):
    username = session.get("username")
    if not username:
        return
    arena.move_player(username, data.get("dx", 0), data.get("dy", 0))
    result = arena.finish_round_if_needed()
    if result:
        store.add_win_reward(result["winner"], result["coins"])
        emit("round_over", result, broadcast=True)
    emit(
        "state_update",
        {"players": arena.players, "hazards": arena.hazards, "round_active": arena.round_active},
        broadcast=True,
    )


def run_server():
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    run_server()
