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
        connection = self.connect()
        try:
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
            connection.commit()
        finally:
            connection.close()

    def create_user(self, username, password):
        connection = self.connect()
        try:
            connection.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            connection.close()

    def get_user(self, username):
        connection = self.connect()
        try:
            row = connection.execute(
                "SELECT username, coins, wins FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            connection.close()

    def verify_user(self, username, password):
        connection = self.connect()
        try:
            row = connection.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            return bool(row and check_password_hash(row["password_hash"], password))
        finally:
            connection.close()

    def add_win_reward(self, username, coins):
        connection = self.connect()
        try:
            connection.execute(
                "UPDATE users SET wins = wins + 1, coins = coins + ? WHERE username = ?",
                (coins, username),
            )
            connection.commit()
        finally:
            connection.close()

    def get_leaderboard(self):
        connection = self.connect()
        try:
            rows = connection.execute(
                "SELECT username, coins, wins FROM users ORDER BY wins DESC, coins DESC, username ASC LIMIT 10"
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            connection.close()
