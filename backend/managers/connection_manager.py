"""
Sushi Go! V2 - WebSocket Connection Manager
This class allows WebSocket communication, enabling real-time multiplayer in browsers
- It tracks active WebSocket connections per game
- It routes all messages to specific players or broadcast it to all
- It handles player connect/disconnect
Connection Manager is just infrastructure, the game logic remains unchanged, and does not know about WebSockets, it gives results and this manager handles the communication.
"""


from typing import Dict
from fastapi import WebSocket

from models import GameState


class ConnectionManager:
    """Manages WebSocket connections for active games, using nested dictionaries to maps player IDs to their WebSocket connections, allowing to route messages to specific players."""
    
    def __init__(self):
        """Initialize with empty connection"""
        # game_code -> {player_id: websocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, game_code: str, player_id: str):
        """
        Accept and register a new WebSocket connection based on the game code and player ID.
        This allows the manager to track which player is connected to which game.
        """
        await websocket.accept()
        if game_code not in self.active_connections:
            self.active_connections[game_code] = {}
        self.active_connections[game_code][player_id] = websocket
    
    def disconnect(self, game_code: str, player_id: str):
        """Remove a WebSocket connection"""
        if game_code in self.active_connections:
            if player_id in self.active_connections[game_code]:
                del self.active_connections[game_code][player_id]
            # Clean up empty games
            if not self.active_connections[game_code]:
                del self.active_connections[game_code]
    
    async def send_personal(self, message: dict, game_code: str, player_id: str):
        """Send a message to one specific player, used for a private information like player's hand"""
        if game_code in self.active_connections:
            if player_id in self.active_connections[game_code]:
                try:
                    await self.active_connections[game_code][player_id].send_json(message)
                except Exception:
                    pass  # Connection may be closed
    
    async def broadcast(self, message: dict, game_code: str, exclude: str = None):
        """Send to all players in game, used for public information like game scoreboard"""

        if game_code in self.active_connections:
            for pid, connection in self.active_connections[game_code].items():
                if pid != exclude:
                    try:
                        await connection.send_json(message)
                    except Exception:
                        pass  # Connection may be closed
    
    async def broadcast_game_state(self, game: GameState):
        """Send personalized game state to each player, to update everyone's screen in their browser."""

        for player_id in game.player_order:
            state = game.get_state(for_player_id=player_id)
            await self.send_personal(
                {"type": "game_state", "data": state}, 
                game.game_code, 
                player_id
            )
    
    def get_connection_count(self, game_code: str) -> int:
        """Get number of active connections for a game"""
        if game_code in self.active_connections:
            return len(self.active_connections[game_code])
        return 0
    
    def is_connected(self, game_code: str, player_id: str) -> bool:
        """Check if a player is connected"""
        if game_code in self.active_connections:
            return player_id in self.active_connections[game_code]
        return False
