"""
Sushi Go! V2 - Game State
GameState is the central controller for a single game instance, managing players, rounds, turns, card selection, and hand passing.
"""

import random
import string
from enum import Enum
from typing import Dict, List, Optional, Any

from models.cards import Card, CardType
from models.deck import Deck
from models.player import Player


class GamePhase(Enum):
    """
    Discrete phases of a game session, the frontend uses this to show appropriate UI.
    
    LOBBY: Waiting for players to join, game not started.
    SELECTING: Players choosing cards from their hands.
    REVEALING: Cards being shown (brief transition phase).
    ROUND_END: Round scored, waiting to start the next round.
    GAME_END: All 3 rounds complete, final scores shown.
    """
    LOBBY = "lobby"
    PLAYING = "playing"
    SELECTING = "selecting"
    REVEALING = "revealing"
    ROUND_END = "round_end"
    GAME_END = "game_end"


def generate_game_code() -> str:
    """
    Generate a 6-character alphanumeric game code, which is short enough to be easily shared while long enough to avoid collisions
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class GameState:
    """
    Complete game state for one game session

        code: Unique game code for joining 
        host_id: Player ID of the game creator 
        players: Dict mapping player_id 
        player_order: List of player_ids in seating order
        phase: Current GamePhase
        round: Current round number 
        turn: Current turn within the round 
        deck: The Deck instance for the current round 
        pass_direction: "left" or "right" for hand passing between rounds
    """
    
    def __init__(self, game_code: str, host_id: str):
        self.game_code = game_code
        self.host_id = host_id
        self.players: Dict[str, Player] = {}
        self.player_order: List[str] = []
        self.phase = GamePhase.LOBBY
        self.current_round = 0
        self.current_turn = 0
        self.deck: Optional[Deck] = None
        self.pass_direction = "left"
    
    def add_player(self, player_id: str, name: str) -> bool:
        """Add a player to the game"""
        if len(self.players) >= 5:
            return False
        if player_id in self.players:
            return False
        
        self.players[player_id] = Player(player_id, name)
        self.player_order.append(player_id)
        return True
    
    def remove_player(self, player_id: str):
        """Remove a player from the game"""
        if player_id in self.players:
            del self.players[player_id]
            self.player_order.remove(player_id)
    
    def can_start(self) -> bool:
        """Check if game can be started"""
        return 2 <= len(self.players) <= 5 and self.phase == GamePhase.LOBBY
    
    def start_game(self) -> bool:
        """The host start the game if possible"""
        if not self.can_start():
            return False
        
        self.current_round = 1
        self._start_round()
        return True
    
    def _start_round(self):
        """Initialize a new round, shuffle deck, deal cards, set direction"""
        self.deck = Deck()
        hands = self.deck.deal(len(self.players))
        
        # Distribute hands and reset player state
        for i, player_id in enumerate(self.player_order):
            player = self.players[player_id]
            player.reset_for_round()
            player.hand = hands[i]
        
        # Set pass direction: left for rounds 1 & 3, right for round 2
        self.pass_direction = "right" if self.current_round == 2 else "left"
        self.current_turn = 1
        self.phase = GamePhase.SELECTING
    
    def select_card(self, player_id: str, card_id: str, 
                    use_chopsticks: bool = False, 
                    second_card_id: str = None) -> bool:
        """Player selects a card from their hand, optionally using chopsticks to select a second card."""

        if self.phase != GamePhase.SELECTING:
            return False
        
        player = self.players.get(player_id)
        if not player:
            return False
        
        # Find the card in hand
        card = self._find_card_in_hand(player, card_id)
        if not card:
            return False
        
        player.selected_card = card
        player.using_chopsticks = False
        player.selected_second_card = None
        
        # Handle chopsticks
        if use_chopsticks and player.has_chopsticks() and second_card_id:
            second_card = self._find_card_in_hand(player, second_card_id)
            if second_card and second_card.id != card_id:
                player.selected_second_card = second_card
                player.using_chopsticks = True
        
        player.is_ready = True
        return True
    
    def _find_card_in_hand(self, player: Player, card_id: str) -> Optional[Card]:
        """Find a card in player's hand by ID"""
        for card in player.hand:
            if card.id == card_id:
                return card
        return None
    
    def all_players_ready(self) -> bool:
        """Check if all players have made their selection"""
        return all(p.is_ready for p in self.players.values())
    
    def reveal_cards(self) -> Dict[str, Any]:
        """
        Reveal all selected cards and process the turn
        """
        if not self.all_players_ready():
            return {}
        
        self.phase = GamePhase.REVEALING
        reveal_data = {}
        
        for player_id, player in self.players.items():
            cards_played = []
            
            if player.selected_card:
                card = player.selected_card
                player.hand.remove(card)
                self._play_card(player, card)
                cards_played.append(card.to_dict())
            
            # Handle second card (if using chopsticks)
            if player.using_chopsticks and player.selected_second_card:
                second_card = player.selected_second_card
                player.hand.remove(second_card)
                self._play_card(player, second_card)
                cards_played.append(second_card.to_dict())
                
                # Return chopsticks to hand
                chopsticks = next(
                    c for c in player.played_cards 
                    if c.card_type == CardType.CHOPSTICKS
                )
                player.played_cards.remove(chopsticks)
                player.hand.append(chopsticks)
            
            reveal_data[player_id] = {
                "cards_played": cards_played,
                "used_chopsticks": player.using_chopsticks
            }
            
            # Reset for next turn
            player.reset_for_turn()
        
        return reveal_data
    
    def _play_card(self, player: Player, card: Card):
        """
        Add a card to player's played cards area
        It can handle special cases like pudding going to separate pudding pile or sushi placed on empty wasabi
        """

        # Handle pudding (kept separately)
        if card.card_type == CardType.PUDDING:
            player.pudding_cards.append(card)
            return
        
        # Check for wasabi (sushi goes on empty wasabi)
        if card.is_sushi():
            empty_wasabi = player.get_empty_wasabi()
            if empty_wasabi:
                card.on_wasabi = True
        
        player.played_cards.append(card)
    
    def pass_hands(self):
        """
        Pass all hands to the next player according to the passing direction
        """
        if len(self.players) < 2:
            return
        
        hands = [self.players[pid].hand for pid in self.player_order]
        
        if self.pass_direction == "left":
            # Each player passes to left (receives from right)
            rotated = hands[1:] + [hands[0]]
        else:
            # Each player passes to right (receives from left)
            rotated = [hands[-1]] + hands[:-1]
        
        for i, pid in enumerate(self.player_order):
            self.players[pid].hand = rotated[i]
    
    def next_turn(self) -> Dict[str, Any]:
        """
        Advance to next turn or end round
        """
        # Check if round is over (no cards left)
        if not self.players[self.player_order[0]].hand:
            return self._end_round()
        
        self.pass_hands()
        self.current_turn += 1
        self.phase = GamePhase.SELECTING
        
        return {"action": "next_turn", "turn": self.current_turn}
    
    def _end_round(self) -> Dict[str, Any]:
        """End the current round (scoring handled by ScoringEngine)"""
        self.phase = GamePhase.ROUND_END
        return {
            "action": "round_end",
            "round": self.current_round
        }
    
    def start_next_round(self) -> Dict[str, Any]:
        """Start the next round or end game"""
        if self.current_round >= 3:
            return self._end_game()
        
        self.current_round += 1
        self._start_round()
        
        return {
            "action": "new_round",
            "round": self.current_round,
            "pass_direction": self.pass_direction
        }
    
    def _end_game(self) -> Dict[str, Any]:
        """End the game"""
        self.phase = GamePhase.GAME_END
        return {"action": "game_end"}
    
    def get_state(self, for_player_id: str = None) -> Dict[str, Any]:
        """
        Convert the game state to a JSON dictionary suitable for WebSocket transmission.
        Used for each player to see their own hand but not others, based on their player ID.
        """
        state = {
            "game_code": self.game_code,
            "phase": self.phase.value,
            "current_round": self.current_round,
            "current_turn": self.current_turn,
            "pass_direction": self.pass_direction,
            "host_id": self.host_id,
            "player_count": len(self.players)
        }
        
        # Include player data
        players_data = []
        for pid in self.player_order:
            player = self.players[pid]
            include_hand = (pid == for_player_id)
            players_data.append(player.to_dict(include_hand=include_hand))
        
        state["players"] = players_data
        
        return state
