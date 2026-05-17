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


if __name__ == "__main__":
    unittest.main()
