import importlib
import unittest
from unittest.mock import Mock, patch

import requests
from appminecraftserver import app
from Game.game.recr import MyGame


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_page_welcomes_player(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "Welcome to the Minecraft Server!"})

    def test_score_endpoint_accepts_score(self):
        response = self.client.post("/score", json={"name": "Recruited Game", "score": 10})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"message": "Score received!", "name": "Recruited Game", "score": 10},
        )


class MyGameTests(unittest.TestCase):
    @patch("Game.game.recr.requests.post")
    def test_send_score_to_server_posts_name_and_score(self, mock_post):
        game = MyGame("Recruited Game")
        game.play()
        mock_post.return_value = Mock(status_code=200)

        response = game.send_score_to_server("http://localhost:5000/score")

        mock_post.assert_called_once_with(
            "http://localhost:5000/score",
            json={"name": "Recruited Game", "score": 10},
            timeout=5,
        )
        self.assertTrue(response)

    @patch("builtins.print")
    @patch("Game.game.recr.requests.post")
    def test_send_score_to_server_explains_how_to_start_server_when_unavailable(
        self, mock_post, mock_print
    ):
        game = MyGame("Recruited Game")
        game.play()
        mock_post.side_effect = requests.ConnectionError("server is offline")

        response = game.send_score_to_server("http://localhost:5000/score")

        self.assertFalse(response)
        mock_print.assert_any_call(
            "Could not reach the score server. Start it with: python run.py server"
        )


class ImportSafetyTests(unittest.TestCase):
    def test_importing_main_does_not_start_game(self):
        main = importlib.import_module("main")

        self.assertTrue(hasattr(main, "run_cube_game"))


if __name__ == "__main__":
    unittest.main()
