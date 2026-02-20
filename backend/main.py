"""
Sushi Go! V2 - FastAPI Server

main.py is the entry point that transforms the terminal game into a web game.
This is where V0 terminal version becomes HTTP endpoints and WebSocket handlers for the web version

Architecture:
- FastAPI handles HTTP requests (create/join game)
- WebSocket handles real-time game updates 
- ConnectionManager routes messages to players
- GameManager tracks active game sessions 
- Models and ScoringEngine handle game logic (same than V0 and V1)
"""

import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from models import GameState, GamePhase
from managers import ConnectionManager, GameManager
from scoring import ScoringEngine

# Initialize FastAPI app
app = FastAPI(title="Sushi Go! Online")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
connection_manager = ConnectionManager()
game_manager = GameManager()

# Static files path
frontend_path = Path(__file__).parent.parent / "frontend"

# Mount static files if frontend exists
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


# ============================================================================
# HTTP Routes
# ============================================================================

@app.get("/")
async def root():
    """Serve the single landing page HTML game interface"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Sushi Go! API - Frontend not found"}


@app.get("/lobby/{game_code}")
async def lobby_page(game_code: str):
    """Create a new game session, requests name and returns the game code with player ID"""
    lobby_path = frontend_path / "lobby.html"
    if lobby_path.exists():
        return FileResponse(lobby_path)
    return {"message": "Lobby page not found"}


@app.get("/game/{game_code}")
async def game_page(game_code: str):
    """Serve the game page"""
    game_path = frontend_path / "game.html"
    if game_path.exists():
        return FileResponse(game_path)
    return {"message": "Game page not found"}


@app.post("/api/create-game")
async def create_game(data: dict):
    """Create a new game and return game code"""
    host_name = data.get("name", "Host")
    
    game_code, host_id, _ = game_manager.create_game(host_name)
    
    return {
        "success": True,
        "game_code": game_code,
        "player_id": host_id,
        "is_host": True
    }


@app.post("/api/join-game")
async def join_game(data: dict):
    """Join existing game, requests game code and name, returns player ID """
    game_code = data.get("game_code", "").upper()
    player_name = data.get("name", "Player")
    
    if not game_manager.game_exists(game_code):
        raise HTTPException(status_code=404, detail="Game not found")
    
    result = game_manager.join_game(game_code, player_name)
    
    if not result:
        game = game_manager.get_game(game_code)
        if game and game.phase != GamePhase.LOBBY:
            raise HTTPException(status_code=400, detail="Game already started")
        raise HTTPException(status_code=400, detail="Could not join game (game may be full)")
    
    player_id, _ = result
    
    return {
        "success": True,
        "game_code": game_code,
        "player_id": player_id,
        "is_host": False
    }


@app.get("/api/game/{game_code}")
async def get_game_info(game_code: str):
    """Get game info"""
    game = game_manager.get_game(game_code)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return game.get_state()


# ============================================================================
# WebSocket Handler
# ============================================================================

@app.websocket("/ws/{game_code}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_code: str, player_id: str):
    """
    WebSocket connection for real-time game updates and communication
    Replaces terminal input/output with WebSocket messages, 
    1. Receives player actions (select a card, host starts the game)  
    2. Sends game state updates (card reveals, round scores, final rankings)
    """
    game = game_manager.get_game(game_code)
    if not game:
        await websocket.close(code=4004)
        return
    
    if player_id not in game.players:
        await websocket.close(code=4003)
        return
    
    # Connect and mark player as connected
    await connection_manager.connect(websocket, game_code, player_id)
    game.players[player_id].is_connected = True
    
    try:
        # Send initial state
        state = game.get_state(for_player_id=player_id)
        await websocket.send_json({"type": "game_state", "data": state})
        
        # Notify other players
        await connection_manager.broadcast(
            {
                "type": "player_connected", 
                "player_id": player_id, 
                "name": game.players[player_id].name
            },
            game_code,
            exclude=player_id
        )
        
        # Broadcast updated state to all
        await connection_manager.broadcast_game_state(game)
        
        # Message loop
        while True:
            data = await websocket.receive_json()
            await handle_message(game_code, player_id, data)
    
    except WebSocketDisconnect:
        connection_manager.disconnect(game_code, player_id)
        if player_id in game.players:
            game.players[player_id].is_connected = False
        await connection_manager.broadcast(
            {"type": "player_disconnected", "player_id": player_id},
            game_code
        )
    except Exception as e:
        print(f"WebSocket error: {e}")
        connection_manager.disconnect(game_code, player_id)


async def handle_message(game_code: str, player_id: str, data: dict):
    """
    Handle incoming WebSocket messages, like game code, player id and action details
    This is the main game logic, replacing V0's sequential pass and play turn structure, with event update handling.
    """
    game = game_manager.get_game(game_code)
    if not game:
        return
    
    action = data.get("action")
    
    if action == "start_game":
        await handle_start_game(game, player_id)
    
    elif action == "select_card":
        await handle_select_card(game, player_id, data)
    
    elif action == "next_round":
        await handle_next_round(game, player_id)


async def handle_start_game(game: GameState, player_id: str):
    """Handle start game request"""
    if player_id != game.host_id:
        await connection_manager.send_personal(
            {"type": "error", "message": "Only host can start"},
            game.game_code, player_id
        )
        return
    
    if not game.can_start():
        await connection_manager.send_personal(
            {"type": "error", "message": "Need 2-5 players"},
            game.game_code, player_id
        )
        return
    
    game.start_game()
    await connection_manager.broadcast({"type": "game_started"}, game.game_code)
    await connection_manager.broadcast_game_state(game)


async def handle_select_card(game: GameState, player_id: str, data: dict):
    """Handle card selection"""
    card_id = data.get("card_id")
    use_chopsticks = data.get("use_chopsticks", False)
    second_card_id = data.get("second_card_id")
    
    if game.select_card(player_id, card_id, use_chopsticks, second_card_id):
        await connection_manager.broadcast(
            {"type": "player_ready", "player_id": player_id},
            game.game_code
        )
        
        # Check if all players ready
        if game.all_players_ready():
            await process_turn(game)
    else:
        await connection_manager.send_personal(
            {"type": "error", "message": "Invalid selection"},
            game.game_code, player_id
        )


async def handle_next_round(game: GameState, player_id: str):
    """Handle next round request"""
    if player_id != game.host_id:
        return
    
    if game.phase == GamePhase.ROUND_END:
        result = game.start_next_round()
        
        if result["action"] == "game_end":
            # Process final scoring
            end_data = game_manager.process_game_end(game)
            await connection_manager.broadcast(
                {"type": "game_end", "data": end_data},
                game.game_code
            )
        else:
            await connection_manager.broadcast(
                {"type": result["action"], "data": result},
                game.game_code
            )
            await connection_manager.broadcast_game_state(game)


async def process_turn(game: GameState):
    """Process card reveals after all players have selected cards, and after a brief pause, advance to the next turn or the round end"""
    # Reveal cards
    reveal_data = game.reveal_cards()
    await connection_manager.broadcast(
        {"type": "cards_revealed", "data": reveal_data},
        game.game_code
    )
    
    # Brief pause for reveal animation
    await asyncio.sleep(2)
    
    # Next turn or end round
    result = game.next_turn()
    
    if result.get("action") == "round_end":
        scores = game_manager.process_round_end(game)
        await connection_manager.broadcast(
            {"type": "round_end", "data": {"round": game.current_round, "scores": scores}},
            game.game_code
        )
        
        # Auto-proceed to game end after round 3
        if game.current_round >= 3:
            await asyncio.sleep(3)
            game.phase = GamePhase.GAME_END
            end_data = game_manager.process_game_end(game)
            await connection_manager.broadcast(
                {"type": "game_end", "data": end_data},
                game.game_code
            )
    else:
        await connection_manager.broadcast_game_state(game)


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup():
    """
    Server startup event message in the terminal
    """
    print("=" * 50)
    print("SUSHI GO! V2 - Web Server started")
    print("=" * 50)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
