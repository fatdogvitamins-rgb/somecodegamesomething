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
