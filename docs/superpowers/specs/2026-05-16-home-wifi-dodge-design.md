# Home Wi-Fi Dodge Game Design

## Goal

Build a local multiplayer game that players on the same home Wi-Fi network can open in a web browser. Players create accounts with usernames and passwords, log in, join a live dodge match together, and compete until one player is left. The winner earns a reward that is stored on their account, and then all players return to the home page.

## Version 1 Summary

Version 1 will be a browser game with:

- Account signup and login
- A home page that shows account info and leaderboard
- A lobby where players gather before a match
- A live dodge game where all connected players move at the same time
- Round-end reward storage for the winner
- Automatic return to the home page after each round

## Main User Flow

1. A player opens the server URL from another device on the same home Wi-Fi network.
2. The player signs up or logs in with a username and password.
3. The player lands on the home page and sees:
   - Their username
   - Their coins
   - Their wins
   - The leaderboard
   - A button to join a match
4. The player enters the lobby and waits for others.
5. When enough players are connected, the match starts.
6. Players move around a small arena while hazards fall from above.
7. If a player is hit, they are eliminated for that round.
8. When one player remains, that player wins the round.
9. The server adds the reward to the winner's account and updates their wins.
10. All players are sent back to the home page and can join another round.

## Game Rules

- The game is a simple top-down 2D dodge game.
- Each player is shown as a small colored square.
- Hazards fall from the top of the arena toward the bottom.
- Players can move in four directions.
- A hit eliminates the player from the current round.
- The last player alive wins.
- The winner receives coins and one additional win.

## Architecture

### Server

The server will use Flask to serve pages and APIs. It will use Flask-SocketIO for live multiplayer communication between devices on the same network.

Server responsibilities:

- Handle signup and login
- Manage sessions for logged-in players
- Keep track of connected players
- Run lobby and round state
- Broadcast live player and hazard updates
- Detect eliminations and winners
- Save account rewards and leaderboard data

### Client

The client will be a browser page built with HTML, CSS, and JavaScript.

Client responsibilities:

- Show login and signup forms
- Display the home page and leaderboard
- Join the lobby
- Send movement input during matches
- Draw players and falling hazards
- Show round results
- Return to the home page when the round ends

### Storage

Version 1 storage will use SQLite on the local machine running the server.

Stored data:

- Username
- Password hash
- Coins
- Wins
- Total games if needed later

The storage code will be kept behind a small database layer so the game can later move to a cloud database without changing the whole app.

## Cloud Upgrade Plan

SQLite is the starting database because it is easy to run on one home computer. When the project grows too large for SQLite, the storage layer should be replaceable with a cloud-backed database such as PostgreSQL or Supabase.

Version 1 will not auto-upload to the cloud. Instead, it will be designed so migration is easy later:

- Keep storage code in one small module
- Avoid SQLite-specific logic in game routes
- Store only simple account and score records
- Make future export and import straightforward

The decision to move to cloud should be based on practical limits such as database size, player count, or wanting internet access outside the home network.

## Pages And Screens

### Home Page

Shows:

- Signup form or login form for logged-out players
- Account stats for logged-in players
- Leaderboard
- Join match button

### Lobby Page

Shows:

- Connected players
- Match status
- Ready or waiting message

### Match Page

Shows:

- The play area
- The local player
- Other players
- Falling hazards
- Alive or eliminated state

## Networking Model

The multiplayer game will use a shared room model:

- Players connect to the same server over home Wi-Fi
- Logged-in players join the active room
- The server is the source of truth for round state
- Clients send input
- The server sends back player positions, hazard positions, eliminations, and winner updates

This keeps multiplayer fair and makes reward handling reliable.

## Reward And Leaderboard Rules

- Only the last surviving player wins the round
- The winner gets a coin reward
- The winner also gets one new win added to their account
- The leaderboard sorts players by wins first, then coins
- After rewards are saved, all players return to the home page

## Error Handling

Version 1 should handle these cases clearly:

- Username already taken during signup
- Wrong password during login
- Player disconnects during lobby
- Player disconnects during a round
- Too few players to start a round
- Server restart clears live round state but keeps saved accounts and rewards

If a player disconnects during a round, they count as eliminated for that round.

## Testing Plan

The project should include tests for:

- Signup validation
- Login success and failure
- Reward saving to accounts
- Leaderboard ordering
- Round winner logic
- Safe database layer behavior

The browser multiplayer rendering itself can be checked manually during development on local devices.

## Out Of Scope For Version 1

These are good future ideas, but not part of the first build:

- Multiple different game modes
- Matchmaking with many rooms
- Chat
- Cosmetic items
- Cloud auto-upload
- Internet-wide hosting outside the home network

## Recommended Build Order

1. Build the account database and auth routes
2. Build the home page and leaderboard
3. Build the lobby flow
4. Build the live dodge round with SocketIO
5. Save rewards and return everyone to the home page
6. Add tests and polish
