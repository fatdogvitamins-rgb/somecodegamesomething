import sys

from appminecraftserver import run_server
from game import run_score_game
from main import run_cube_game


def main():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "help"

    if mode == "server":
        run_server()
    elif mode == "web":
        run_server()
    elif mode == "score":
        run_score_game()
    elif mode == "cube":
        run_cube_game()
    elif mode == "all":
        run_score_game()
        run_cube_game()
        run_server()
    else:
        print("Pick one of these:")
        print("python run.py server")
        print("python run.py web")
        print("python run.py score")
        print("python run.py cube")
        print("python run.py all")


if __name__ == "__main__":
    main()
