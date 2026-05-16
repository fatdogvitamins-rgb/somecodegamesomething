from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Minecraft Server!"})


@app.route("/score", methods=["POST"])
def receive_score():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    score = data.get("score")

    if not isinstance(name, str) or not isinstance(score, int):
        return jsonify({"error": "Send a player name and a whole-number score."}), 400

    return jsonify({"message": "Score received!", "name": name, "score": score})


def run_server():
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    run_server()
