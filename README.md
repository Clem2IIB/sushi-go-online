# Sushi Go! Online

A web-based multiplayer implementation of the popular card drafting game Sushi Go! by Phil Walker-Harding.
Play with 2-5 players in real-time from different devices on your local network.
Check the RULEBOOK.md file to understand the game rules and how to play.

---

## Installation

### Setup

```bash
# Clone the repository
git clone https://github.com/Clem2IIB/sushi-go-online.git
cd sushi-go-online
```

**Create a virtual environment:**
```bash
# On Windows, run:
python -m venv .venv    # to create a virtual environment folder
.venv\Scripts\activate  # to activate the virtual environment in your terminal
# if running scripts are disabled, run this command beforehand
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# On MacOS, run:
python3 -m venv .venv   # to create a virtual environment folder
source .venv/bin/activate   # to activate the virtual environment in your terminal
```

**Install python requirements:**
```bash
pip install -r requirements.txt
```

It will install all needed libraries in your virtual environment for the game to run properly:
- `fastapi` - for the web framework
- `uvicorn` - for the server
- `websockets` - for real-time player communication with the server

---

## Running the Server

```bash
# Navigate to backend folder
cd backend

# Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

You should now see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

To stop the server, press `Ctrl+C` in the terminal.

---

## Playing the Game

### Creating a game for the host player

1. Open your browser to: `http://localhost:8000`
2. Under "Create New Game":
   - Enter your name
   - Click **Create Game**
3. You'll see a 6-character game code (for example, `ABC123`)

### Joining a game for the other players

1. Open `http://localhost:8000` (in another tab or device)
2. Under "Join Existing Game":
   - Enter the game code given by the host
   - Enter your name
   - Click **Join Game**
3. You have to wait for all players to join, only the host sees the **Start Game** button, and you need at least 2 players to start

### Playing on the same computer

Open multiple browser tabs to `http://localhost:8000`, each tab is a different player. Switch between each tab for each player to play their hand. (Not the best setup for several players, but it is working)

### Playing on different devices (LAN gameplay)

This is the best gameplay if you have several players with their own laptop.

1. For the host, find your computer's local IP address:
   - Windows: `Get-NetIPAddress -AddressFamily IPv4`
   - Mac/Linux: `ipconfig getifaddr en0` (WiFi) or `ipconfig getifaddr en1` (Ethernet)
   - You should get something like this: `192.168.1.100`
   - Then, start the server as shown above, and send this link to other players: `http://YOUR_IP:8000` (keeping the example `http://192.168.1.100:8000`)

2. For other players, connect to the IP address link: `http://HOST_IP:8000`

3. All devices must be on the **same WiFi/network**

### Gameplay flow

1. **Click on a card** in your hand to select it
2. To use chopsticks, select your first card, a prompt asks you if you want to select a second card, then click your second card
3. Click **Confirm Selection**, your selection is locked, just wait for other players to play, and play the game until the end

---

## Card Images

The game uses PNG card images located in `frontend/assets/cards/`. Make sure these files exist:
- `maki_1.png`, `maki_2.png`, `maki_3.png`
- `tempura.png`, `sashimi.png`, `dumpling.png`
- `salmon_sushi.png`, `squid_sushi.png`, `egg_sushi.png`
- `wasabi.png`, `chopsticks.png`, `pudding.png`

---

## Project Structure

```
sushi-go-online/
├── backend/
│   ├── managers/
│   │   ├── __init__.py
│   │   ├── connection_manager.py    # WebSocket connection handling for multiple players
│   │   └── game_manager.py          # Game management from game creation, joining and game ending
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cards.py                 # Card and CardType classes for each card type
│   │   ├── deck.py                  # Deck management for the 108 cards
│   │   ├── game_state.py            # Game state and phases of the game
│   │   └── player.py                # Player class to handle multiple players
│   ├── scoring/
│   │   ├── __init__.py
│   │   └── scoring_engine.py        # All scoring logic specific to each card type
│   ├── __init__.py
│   └── main.py                      # FastAPI application
├── frontend/
│   ├── assets/
│   │   └── cards/                   # Card images png
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── api.js                   # HTTP API calls
│   │   ├── game.js                  # Main game controller
│   │   ├── lobby.js                 # Lobby functionality
│   │   ├── ui.js                    # UI rendering
│   │   └── websocket.js             # WebSocket handling
│   ├── game.html                    # Game interface
│   ├── index.html                   # First landing page
│   └── lobby.html                   # Pre-game lobby
├── requirements.txt
├── README.md
└── RULEBOOK.md
```

---

## Now check the RULEBOOK.md to understand the full game rules and scoring: Enjoy!