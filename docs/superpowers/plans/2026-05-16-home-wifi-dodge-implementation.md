# Home Wi-Fi Dodge Game Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a home-Wi-Fi browser dodge game with signup/login, leaderboard, live match flow, winner rewards, and return-to-home behavior.

**Architecture:** Keep the Flask app as the main entrypoint, add a small SQLite storage module for accounts and leaderboard data, and add Socket.IO-driven round state for the live dodge arena. The browser UI will be plain HTML/CSS/JavaScript so phones and laptops on the same Wi-Fi can open it without installing anything.

**Tech Stack:** Python, Flask, Flask-SocketIO, SQLite, HTML, CSS, JavaScript, `unittest`

---

## File Structure

- Modify: `appminecraftserver.py`
  - Keep the Flask app entrypoint
  - Add auth routes, page routes, and Socket.IO event hooks
- Modify: `run.py`
  - Add a clearer game/server mode for the browser version
- Create: `storage.py`
  - SQLite access layer for users, rewards, and leaderboard reads
- Create: `arena.py`
  - Round state, player state, hazard spawning, and winner logic
- Create: `templates/home.html`
  - Signup/login page plus logged-in home page
- Create: `templates/lobby.html`
  - Waiting room screen before the match starts
- Create: `templates/game.html`
  - Canvas page for the live dodge game
- Create: `static/game.js`
  - Socket.IO client, movement input, rendering, and round-end redirect
- Create: `static/style.css`
  - Shared page styling
- Create: `tests/test_storage.py`
  - Storage-layer tests
- Create: `tests/test_auth_pages.py`
  - Signup/login/home-page tests
- Create: `tests/test_arena.py`
  - Winner logic and reward-flow tests

### Task 1: Add the SQLite storage layer

**Files:**
- Create: `storage.py`
- Test: `tests/test_storage.py`

- [ ] **Step 1: Write the failing test**

```python
import tempfile
import unittest

from storage import AccountStore


class AccountStoreTests(unittest.TestCase):
    def test_create_user_and_leaderboard(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as db_file:
            store = AccountStore(db_file.name)
            store.initialize()

            created = store.create_user("alex", "secret123")

            self.assertTrue(created)
            profile = store.get_user("alex")
            self.assertEqual(profile["username"], "alex")
            self.assertEqual(profile["coins"], 0)
            self.assertEqual(profile["wins"], 0)
            self.assertEqual(store.get_leaderboard()[0]["username"], "alex")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest tests.test_storage -v`

Expected: `FAIL` with `ModuleNotFoundError: No module named 'storage'`

- [ ] **Step 3: Write minimal implementation**

```python
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash


class AccountStore:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    coins INTEGER NOT NULL DEFAULT 0,
                    wins INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def create_user(self, username, password):
        try:
            with self.connect() as connection:
                connection.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT username, coins, wins FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        return dict(row) if row else None

    def verify_user(self, username, password):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        return bool(row and check_password_hash(row["password_hash"], password))

    def add_win_reward(self, username, coins):
        with self.connect() as connection:
            connection.execute(
                "UPDATE users SET wins = wins + 1, coins = coins + ? WHERE username = ?",
                (coins, username),
            )

    def get_leaderboard(self):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT username, coins, wins FROM users ORDER BY wins DESC, coins DESC, username ASC LIMIT 10"
            ).fetchall()
        return [dict(row) for row in rows]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest tests.test_storage -v`

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add storage.py tests/test_storage.py
git commit -m "feat: add account storage layer"
```

### Task 2: Add signup, login, and the home page

**Files:**
- Modify: `appminecraftserver.py`
- Create: `templates/home.html`
- Create: `static/style.css`
- Test: `tests/test_auth_pages.py`

- [ ] **Step 1: Write the failing test**

```python
import os
import tempfile
import unittest

os.environ["APP_DB_PATH"] = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name

from appminecraftserver import app, store


class AuthPageTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.secret_key = "test-secret"
        store.initialize()
        self.client = app.test_client()

    def test_signup_creates_account_and_redirects_home(self):
        response = self.client.post(
            "/signup",
            data={"username": "alex", "password": "secret123"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome, alex", response.data)
        self.assertIn(b"Coins: 0", response.data)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest tests.test_auth_pages -v`

Expected: `FAIL` because `/signup` and the HTML page do not exist yet

- [ ] **Step 3: Write minimal implementation**

```python
# appminecraftserver.py
import os

from flask import Flask, redirect, render_template, request, session, url_for

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
        return render_template("home.html", profile=None, leaderboard=leaderboard, error="Pick a name and a longer password."), 400
    if not store.create_user(username, password):
        leaderboard = store.get_leaderboard()
        return render_template("home.html", profile=None, leaderboard=leaderboard, error="That username is already taken."), 400
    session["username"] = username
    return redirect(url_for("home"))


@app.post("/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not store.verify_user(username, password):
        leaderboard = store.get_leaderboard()
        return render_template("home.html", profile=None, leaderboard=leaderboard, error="Wrong username or password."), 400
    session["username"] = username
    return redirect(url_for("home"))
```

```html
<!-- templates/home.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Home Wi-Fi Dodge</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <main class="page">
    <h1>Home Wi-Fi Dodge</h1>
    {% if error %}
    <p class="error">{{ error }}</p>
    {% endif %}

    {% if profile %}
    <section class="card">
      <h2>Welcome, {{ profile.username }}</h2>
      <p>Coins: {{ profile.coins }}</p>
      <p>Wins: {{ profile.wins }}</p>
      <a class="button" href="{{ url_for('lobby_page') }}">Join Match</a>
    </section>
    {% else %}
    <section class="grid">
      <form class="card" method="post" action="/signup">
        <h2>Sign Up</h2>
        <input name="username" placeholder="Username" required>
        <input name="password" placeholder="Password" type="password" required>
        <button type="submit">Create Account</button>
      </form>
      <form class="card" method="post" action="/login">
        <h2>Log In</h2>
        <input name="username" placeholder="Username" required>
        <input name="password" placeholder="Password" type="password" required>
        <button type="submit">Log In</button>
      </form>
    </section>
    {% endif %}

    <section class="card">
      <h2>Leaderboard</h2>
      <ol>
        {% for player in leaderboard %}
        <li>{{ player.username }} - {{ player.wins }} wins - {{ player.coins }} coins</li>
        {% else %}
        <li>No players yet.</li>
        {% endfor %}
      </ol>
    </section>
  </main>
</body>
</html>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest tests.test_auth_pages -v`

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add appminecraftserver.py templates/home.html static/style.css tests/test_auth_pages.py
git commit -m "feat: add auth pages and home screen"
```

### Task 3: Add the arena rules module

**Files:**
- Create: `arena.py`
- Test: `tests/test_arena.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest

from arena import DodgeArena


class DodgeArenaTests(unittest.TestCase):
    def test_last_alive_player_is_winner(self):
        arena = DodgeArena(width=480, height=320, reward_coins=25)
        arena.add_player("alex")
        arena.add_player("jamie")
        arena.eliminate_player("jamie")

        winner = arena.get_winner()

        self.assertEqual(winner, "alex")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest tests.test_arena -v`

Expected: `FAIL` with `ModuleNotFoundError: No module named 'arena'`

- [ ] **Step 3: Write minimal implementation**

```python
import random


class DodgeArena:
    def __init__(self, width, height, reward_coins):
        self.width = width
        self.height = height
        self.reward_coins = reward_coins
        self.players = {}
        self.hazards = []
        self.round_active = False

    def add_player(self, username):
        self.players[username] = {"x": self.width // 2, "y": self.height - 40, "alive": True}

    def remove_player(self, username):
        self.players.pop(username, None)

    def start_round(self):
        self.round_active = True
        self.hazards = []
        for player in self.players.values():
            player["alive"] = True
            player["x"] = random.randint(40, self.width - 40)
            player["y"] = self.height - 40

    def move_player(self, username, dx, dy):
        player = self.players.get(username)
        if not player or not player["alive"]:
            return
        player["x"] = max(20, min(self.width - 20, player["x"] + dx))
        player["y"] = max(20, min(self.height - 20, player["y"] + dy))

    def eliminate_player(self, username):
        if username in self.players:
            self.players[username]["alive"] = False

    def alive_players(self):
        return [name for name, player in self.players.items() if player["alive"]]

    def get_winner(self):
        alive = self.alive_players()
        if len(alive) == 1:
            return alive[0]
        return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest tests.test_arena -v`

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add arena.py tests/test_arena.py
git commit -m "feat: add dodge arena state"
```

### Task 4: Add lobby and game pages

**Files:**
- Modify: `appminecraftserver.py`
- Create: `templates/lobby.html`
- Create: `templates/game.html`
- Modify: `static/style.css`
- Test: `tests/test_auth_pages.py`

- [ ] **Step 1: Write the failing test**

```python
def test_logged_in_player_can_open_lobby_page(self):
    with self.client.session_transaction() as session_data:
        session_data["username"] = "alex"

    response = self.client.get("/lobby")

    self.assertEqual(response.status_code, 200)
    self.assertIn(b"Waiting for players", response.data)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest tests.test_auth_pages -v`

Expected: `FAIL` with `404` for `/lobby`

- [ ] **Step 3: Write minimal implementation**

```python
# appminecraftserver.py
from flask import abort


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
```

```html
<!-- templates/lobby.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Lobby</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <main class="page">
    <section class="card">
      <h1>Waiting for players</h1>
      <p>{{ username }}, stay here until the round starts.</p>
      <a class="button" href="{{ url_for('game_page') }}">Enter Arena</a>
    </section>
  </main>
</body>
</html>
```

```html
<!-- templates/game.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dodge Arena</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <main class="page">
    <section class="card arena-card">
      <h1>Dodge Arena</h1>
      <p id="status">Move and survive.</p>
      <canvas id="arena" width="480" height="320"></canvas>
    </section>
    <script>
      window.GAME_USERNAME = "{{ username }}";
    </script>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script src="{{ url_for('static', filename='game.js') }}"></script>
  </main>
</body>
</html>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest tests.test_auth_pages -v`

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add appminecraftserver.py templates/lobby.html templates/game.html static/style.css tests/test_auth_pages.py
git commit -m "feat: add lobby and game pages"
```

### Task 5: Add live multiplayer Socket.IO flow

**Files:**
- Modify: `appminecraftserver.py`
- Modify: `arena.py`
- Create: `static/game.js`
- Test: `tests/test_arena.py`

- [ ] **Step 1: Write the failing test**

```python
def test_winner_gets_reward_and_round_resets(self):
    arena = DodgeArena(width=480, height=320, reward_coins=25)
    arena.add_player("alex")
    arena.add_player("jamie")
    arena.start_round()
    arena.eliminate_player("jamie")

    result = arena.finish_round_if_needed()

    self.assertEqual(result["winner"], "alex")
    self.assertEqual(result["coins"], 25)
    self.assertFalse(arena.round_active)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest tests.test_arena -v`

Expected: `FAIL` because `finish_round_if_needed` does not exist yet

- [ ] **Step 3: Write minimal implementation**

```python
# arena.py
    def finish_round_if_needed(self):
        winner = self.get_winner()
        if not winner:
            return None
        self.round_active = False
        return {"winner": winner, "coins": self.reward_coins}
```

```python
# appminecraftserver.py
from flask_socketio import SocketIO, emit

from arena import DodgeArena

socketio = SocketIO(app, cors_allowed_origins="*")
arena = DodgeArena(width=480, height=320, reward_coins=25)


@socketio.on("join_game")
def handle_join_game(data):
    username = session.get("username")
    if not username:
        return
    arena.add_player(username)
    if len(arena.players) >= 2 and not arena.round_active:
        arena.start_round()
    emit("state_update", {"players": arena.players, "hazards": arena.hazards, "round_active": arena.round_active}, broadcast=True)


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
    emit("state_update", {"players": arena.players, "hazards": arena.hazards, "round_active": arena.round_active}, broadcast=True)
```

```javascript
// static/game.js
const socket = io();
const canvas = document.getElementById("arena");
const context = canvas.getContext("2d");
const statusNode = document.getElementById("status");
const state = { players: {}, hazards: [] };

socket.emit("join_game", { username: window.GAME_USERNAME });

window.addEventListener("keydown", (event) => {
  const moves = {
    ArrowLeft: { dx: -12, dy: 0 },
    ArrowRight: { dx: 12, dy: 0 },
    ArrowUp: { dx: 0, dy: -12 },
    ArrowDown: { dx: 0, dy: 12 },
    a: { dx: -12, dy: 0 },
    d: { dx: 12, dy: 0 },
    w: { dx: 0, dy: -12 },
    s: { dx: 0, dy: 12 },
  };
  const move = moves[event.key];
  if (move) {
    socket.emit("move", move);
  }
});

socket.on("state_update", (nextState) => {
  state.players = nextState.players;
  state.hazards = nextState.hazards;
  statusNode.textContent = nextState.round_active ? "Round live! Dodge!" : "Waiting for more players.";
  draw();
});

socket.on("round_over", (result) => {
  statusNode.textContent = `${result.winner} wins ${result.coins} coins! Going home...`;
  setTimeout(() => {
    window.location.href = "/";
  }, 2500);
});

function draw() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  Object.entries(state.players).forEach(([username, player]) => {
    context.fillStyle = player.alive ? (username === window.GAME_USERNAME ? "#ff6b6b" : "#4dabf7") : "#868e96";
    context.fillRect(player.x - 12, player.y - 12, 24, 24);
  });
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest tests.test_arena -v`

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add appminecraftserver.py arena.py static/game.js tests/test_arena.py
git commit -m "feat: add live dodge round flow"
```

### Task 6: Add reward display, browser-friendly score route, and end-to-end checks

**Files:**
- Modify: `appminecraftserver.py`
- Modify: `templates/home.html`
- Modify: `tests/test_game_server.py`
- Modify: `run.py`

- [ ] **Step 1: Write the failing test**

```python
def test_score_page_explains_post_only_in_browser(self):
    response = self.client.get("/score")

    self.assertEqual(response.status_code, 200)
    self.assertEqual(
        response.get_json(),
        {"message": "Use POST to send scores here."},
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest tests.test_game_server -v`

Expected: `FAIL` because `/score` only allows `POST`

- [ ] **Step 3: Write minimal implementation**

```python
# appminecraftserver.py
@app.route("/score", methods=["GET", "POST"])
def receive_score():
    if request.method == "GET":
        return jsonify({"message": "Use POST to send scores here."})

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    score = data.get("score")

    if not isinstance(name, str) or not isinstance(score, int):
        return jsonify({"error": "Send a player name and a whole-number score."}), 400

    return jsonify({"message": "Score received!", "name": name, "score": score})
```

```python
# run.py
    elif mode == "web":
        run_server()
```

```html
<!-- templates/home.html -->
<p class="tip">Open this server from another device on your Wi-Fi with your computer's local IP address.</p>
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `c:\Users\fatdo\something\.venv\Scripts\python.exe -m unittest discover -s tests`

Expected: `OK`

- [ ] **Step 5: Manual smoke test**

Run:

```bash
c:\Users\fatdo\something\.venv\Scripts\python.exe c:/Users/fatdo/something/run.py server
```

Expected:
- `http://localhost:5000/` opens the home page
- Two browsers can log in with different accounts
- Both can open `/game`
- One winner gets coins and a win
- Both return to home page after the round

- [ ] **Step 6: Commit**

```bash
git add appminecraftserver.py templates/home.html tests/test_game_server.py run.py
git commit -m "feat: polish dodge web game flow"
```

## Self-Review

- Spec coverage:
  - Signup/login: Task 2
  - Home page with leaderboard: Task 2
  - Lobby and match pages: Task 4
  - Live shared round: Task 5
  - Winner rewards and return home: Task 5 and Task 6
  - SQLite-first storage with upgrade-friendly boundary: Task 1
- Placeholder scan:
  - No `TODO`, `TBD`, or vague “handle later” language remains in the task steps
- Type consistency:
  - `AccountStore`, `DodgeArena`, `add_win_reward`, `get_leaderboard`, and `finish_round_if_needed` use consistent names across tasks
