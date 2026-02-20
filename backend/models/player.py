"""
Sushi Go! V2 - Player Model
Holds all state for 1 player: their hand, played cards, score, and current turn selections.
It is a data structure that get serialized to JSON and sent to the frontend for rendering
In V2 we need to store the selections because the server waits for all players to select before revealing
Using unique player IDs to identify players, for Websocket routing and player identification
"""
from dataclasses import dataclass, field
from typing import List, Optional

from models.cards import Card, CardType


@dataclass
class Player:
    """
    Represents a player complete state during a game flow
    
        player_id: Unique identifier 
        name: Display the name chosen by the player
        hand: Cards currently in hand (only shown to this player).
        played_cards: Cards played this round (visible to all players).
        pudding_cards: Puddings collected by this player
        score: Total accumulated points.
        round_scores: Points earned in each round [R1, R2, R3].
        selected_card: Card chosen this turn (before reveal).
        selected_second_card: Second card if using chopsticks
        using_chopsticks: Whether player is using chopsticks this turn
        is_ready: True when player has confirmed their selection.
    """
    
    player_id: str
    name: str
    hand: List[Card] = field(default_factory=list)
    played_cards: List[Card] = field(default_factory=list)
    pudding_cards: List[Card] = field(default_factory=list)
    score: int = 0
    round_scores: List[int] = field(default_factory=lambda: [0, 0, 0])
    selected_card: Optional[Card] = None
    selected_second_card: Optional[Card] = None  # For chopsticks
    using_chopsticks: bool = False
    is_ready: bool = False
    is_connected: bool = True
    
    def has_chopsticks(self) -> bool:
        """Check if player has chopsticks available in his played cards"""
        return any(c.card_type == CardType.CHOPSTICKS for c in self.played_cards)
    
    def get_empty_wasabi(self) -> List[Card]:
        """
        Return wasabi cards that don't have sushi on them yet
        
        A wasabi is "used" when a sushi card has on_wasabi=True
        """
        wasabi_cards = [c for c in self.played_cards if c.card_type == CardType.WASABI]
        sushi_on_wasabi_count = sum(
            1 for c in self.played_cards 
            if c.is_sushi() and c.on_wasabi
        )
        return wasabi_cards[:max(0, len(wasabi_cards) - sushi_on_wasabi_count)]
    
    def count_maki_symbols(self) -> int:
        """Count total maki symbols from played cards"""
        return sum(c.maki_count for c in self.played_cards if c.card_type == CardType.MAKI)
    
    def count_card_type(self, card_type: CardType) -> int:
        """Count how many played cards of a specific type the player has."""
        return sum(1 for c in self.played_cards if c.card_type == card_type)
    
    def reset_for_round(self):
        """Clear player state for a new round, except for puddings that persist accross rounds"""
        self.hand = []
        self.played_cards = []
        self.selected_card = None
        self.selected_second_card = None
        self.using_chopsticks = False
        self.is_ready = False
    
    def reset_for_turn(self):
        """Clear player turn state after cards are revealed"""
        self.selected_card = None
        self.selected_second_card = None
        self.using_chopsticks = False
        self.is_ready = False
    
    def to_dict(self, include_hand: bool = False) -> dict:
        """Convert player state to a JSON dictionary suitable for Websocket transmission"""
        
        data = {
            "player_id": self.player_id,
            "name": self.name,
            "score": self.score,
            "round_scores": self.round_scores,
            "played_cards": [c.to_dict() for c in self.played_cards],
            "pudding_count": len(self.pudding_cards),
            "hand_count": len(self.hand),
            "is_ready": self.is_ready,
            "is_connected": self.is_connected,
            "has_chopsticks": self.has_chopsticks()
        }
        if include_hand:
            data["hand"] = [c.to_dict() for c in self.hand]
        return data
