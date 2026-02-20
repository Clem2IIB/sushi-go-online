"""
Sushi Go! V2 - Game Manager
Handles multiple concurrent games by creating new game sessions with unique codes, handling player joining, and managing the games databases (in-memory for simplicity)

GameState manages ONE game's internal logic while GameManager manages the COLLECTION of all active games.
"""
from typing import Dict, Optional, Tuple

from models import GameState, GamePhase
from models.game_state import generate_game_code
from scoring import ScoringEngine


class GameManager:
    """
    Manages multiple concurrent games identified by unique codes.
    It handles:
    - Game creation
    - Player joining
    - Game lifecycle
    - Score calculation
    """
    
    def __init__(self):
        """Initialize with empty game registry."""
        self.games: Dict[str, GameState] = {}
    
    def create_game(self, host_name: str) -> Tuple[str, str, str]:
        """Create a new game session, returns (game_code, host_player_id) to identify the game and host player in future websocket messages"""

        # Generate unique game code
        game_code = generate_game_code()
        while game_code in self.games:
            game_code = generate_game_code()
        
        # Generate host player ID
        host_id = f"player_{generate_game_code()}"
        
        # Create game
        game = GameState(game_code, host_id)
        game.add_player(host_id, host_name)
        self.games[game_code] = game
        
        return game_code, host_id, host_name
    
    def join_game(self, game_code: str, player_name: str) -> Optional[Tuple[str, str]]:
        """Add a player to an existing game, return player_id if successful connection or None if failed"""

        game = self.games.get(game_code)
        if not game:
            return None
        
        if game.phase != GamePhase.LOBBY:
            return None
        
        if len(game.players) >= 5:
            return None
        
        # Generate player ID
        player_id = f"player_{generate_game_code()}"
        
        if not game.add_player(player_id, player_name):
            return None
        
        return player_id, player_name
    
    def get_game(self, game_code: str) -> Optional[GameState]:
        """Retrieve a game session by its unique code."""
        return self.games.get(game_code)
    
    def game_exists(self, game_code: str) -> bool:
        """Check if a game exists"""
        return game_code in self.games
    
    def start_game(self, game_code: str, player_id: str) -> bool:
        """
        Start a game for the given game code if the requesting player is the host
        """

        game = self.games.get(game_code)
        if not game:
            return False
        
        if player_id != game.host_id:
            return False
        
        return game.start_game()
    
    def process_round_end(self, game: GameState) -> Dict:
        """
        Process end of round scoring
        """
        scores = ScoringEngine.score_round(list(game.players.values()))
        ScoringEngine.apply_round_scores(
            list(game.players.values()), 
            scores, 
            game.current_round
        )
        return scores
    
    def process_game_end(self, game: GameState) -> Dict:
        """Score the pudding at the end of the game and return pudding scores and final rankings"""
        
        # Score pudding
        pudding_scores = ScoringEngine.score_pudding(
            list(game.players.values()),
            is_two_player=(len(game.players) == 2)
        )
        ScoringEngine.apply_pudding_scores(
            list(game.players.values()), 
            pudding_scores
        )
        
        # Get rankings
        rankings = ScoringEngine.get_rankings(list(game.players.values()))
        
        return {
            "pudding_scores": pudding_scores,
            "rankings": rankings,
            "winner": rankings[0]["name"] if rankings else None
        }
    
    def remove_game(self, game_code: str):
        """Remove a game from the manager"""
        if game_code in self.games:
            del self.games[game_code]
    
    def get_active_game_count(self) -> int:
        """Get number of active games"""
        return len(self.games)
