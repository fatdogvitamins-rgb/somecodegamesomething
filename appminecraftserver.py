import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from storage import AccountStore

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY", "dev-secret")
store = AccountStore(os.environ.get("APP_DB_PATH", "players.db"))
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


@app.route("/score", methods=["POST"])
def receive_score():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    score = data.get("score")

    if not isinstance(name, str) or not isinstance(score, int):
        return jsonify({"error": "Send a player name and a whole-number score."}), 400

    return jsonify({"message": "Score received!", "name": name, "score": score})


def run_server():
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    run_server()
