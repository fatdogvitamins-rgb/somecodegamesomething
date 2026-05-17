import os
import tempfile
import unittest

from storage import AccountStore


class AccountStoreTests(unittest.TestCase):
    def test_create_user_and_leaderboard(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "players.db")
            store = AccountStore(db_path)
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
