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
