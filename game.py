import Game.game.recr as recr


def run_score_game(server_url="http://localhost:5000/score"):
    recruited_game = recr.MyGame("Recruited Game")
    recruited_game.play()
    print(f"Current score: {recruited_game.get_score()}")
    recruited_game.send_score_to_server(server_url)


if __name__ == "__main__":
    run_score_game()
