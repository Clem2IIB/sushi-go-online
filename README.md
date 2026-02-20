# Sushi Go! - V2 Installation Guide

This README.md covers setup and running instructions for the V2 of the Sushi Go! game.
Check the `RULEBOOK.md` file to understand how to play

---

## V2 Polished Web Local Version

### Setup

0. **Extract the zip file : `sushi_go_v2`**
In your terminal, navigate to the v2 folder:
```bash
# On Windows, run:
cd $HOME\\*Downloads*\\sushi_go_v2  # or the folder where you extracted the zip-file

# On MacOS, run:
cd ~/Downloads/sushi_go_v2    # or the folder where you extracted the zip-file
```

1. **Create a virtual environment:**
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

2. **Install python requirements:**
```bash
pip install -r requirements.txt
```

It will install all needed libraries in your virtual environment for the game to run properly:
- `fastapi` - for the web framework
- `uvicorn` - for the server
- `websockets` - for real-time player communication with the server

### Running the Server

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

### Playing the Game


**On the same computer:** (Not the best setup for several players, but it is working)
- Open your browser to: `http://localhost:8000`, and create a game as the host
- For multiple players on the same computer, open multiple browser tabs to `http://localhost:8000`, each tab is a different player
- Now each player has its own tab, and you can switch between each tab for each player to play his hand


**Players on different devices (LAN gameplay play):** (Best gameplay if you have several players with their own laptop)

1. For the host, find your computer's local IP address:
   - Windows: `Get-NetIPAddress -AddressFamily IPv4` 
   - Mac/Linux: `ipconfig getifaddr en0`(if you're on WIFI) or `ipconfig getifaddr en1` (if you're on Ethernet) in your terminal
   - You should get something like this :  `192.168.1.100`
   - Then, start the server as shown above, and send this new link to other players `http://YOUR_IP:8000` (keeping the example `http://192.168.1.100:8000`)

2. For other players connect to the new IP address link: `http://HOST_IP:8000` (keeping the example, connect to `http://192.168.1.100:8000`)

3. All devices must be on the **same WiFi/network**


### Stopping the Server

Press `Ctrl+C` in the terminal.


### Card Images

The V2 version requires PNG card images in `frontend/assets/cards/`. Make sure to check that these files exist:
- `maki_1.png`, `maki_2.png`, `maki_3.png`
- `tempura.png`, `sashimi.png`, `dumpling.png`
- `salmon_sushi.png`, `squid_sushi.png`, `egg_sushi.png`
- `wasabi.png`, `chopsticks.png`, `pudding.png`

---

## Now check the RULEBOOK.md to understand how to play the game: Enjoy!

---

## Project Structure

``` bash
sushi_go/
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
└── README.md
└── RULEBOOK.md
```