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

    def test_logged_in_player_can_open_lobby_page(self):
        with self.client.session_transaction() as session_data:
            session_data["username"] = "alex"

        response = self.client.get("/lobby")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Waiting for players", response.data)


if __name__ == "__main__":
    unittest.main()
