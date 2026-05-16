import requests


class MyGame:
    def __init__(self, name):
        self.name = name
        self.score = 0

    def play(self):
        # Simulate playing the game and updating the score
        self.score += 10
        print(f"{self.name} played! Current score: {self.score}")

    def get_score(self):
        return self.score

    def send_score_to_server(self, url):
        data = {"name": self.name, "score": self.score}

        try:
            response = requests.post(url, json=data, timeout=5)
        except requests.RequestException as error:
            print(f"Could not reach the server: {error}")
            return False

        if response.status_code == 200:
            print("Score sent successfully!")
            return True
        else:
            print("Failed to send score.")
            return False

