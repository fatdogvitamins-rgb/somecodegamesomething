const socket = io();
const canvas = document.getElementById("arena");
const context = canvas.getContext("2d");
const statusNode = document.getElementById("status");
const state = { players: {}, hazards: [] };

socket.emit("join_game", { username: window.GAME_USERNAME });

window.addEventListener("keydown", (event) => {
  const moves = {
    ArrowLeft: { dx: -12, dy: 0 },
    ArrowRight: { dx: 12, dy: 0 },
    ArrowUp: { dx: 0, dy: -12 },
    ArrowDown: { dx: 0, dy: 12 },
    a: { dx: -12, dy: 0 },
    d: { dx: 12, dy: 0 },
    w: { dx: 0, dy: -12 },
    s: { dx: 0, dy: 12 },
  };
  const move = moves[event.key];
  if (move) {
    socket.emit("move", move);
  }
});

socket.on("state_update", (nextState) => {
  state.players = nextState.players;
  state.hazards = nextState.hazards;
  statusNode.textContent = nextState.round_active ? "Round live! Dodge!" : "Waiting for more players.";
  draw();
});

socket.on("round_over", (result) => {
  statusNode.textContent = `${result.winner} wins ${result.coins} coins! Going home...`;
  setTimeout(() => {
    window.location.href = "/";
  }, 2500);
});

function draw() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  Object.entries(state.players).forEach(([username, player]) => {
    context.fillStyle = player.alive ? (username === window.GAME_USERNAME ? "#ff6b6b" : "#4dabf7") : "#868e96";
    context.fillRect(player.x - 12, player.y - 12, 24, 24);
  });
}
