"""
Sushi Go! V2 - Deck 

This module defines the Deck class which creates and manages the deck of 108 cards used in the game.
It defines the methods to shuffle the deck and deal hands to players.
"""

import random
from typing import List

from models.cards import Card, CardType


class Deck:
    """
    Manages the 108-card deck per official Sushi Go! rules
    
    Card distribution:
    - 14 Tempura
    - 14 Sashimi
    - 14 Dumpling
    - 6 Maki (1 symbol)
    - 12 Maki (2 symbols)
    - 8 Maki (3 symbols)
    - 10 Salmon Sushi
    - 5 Squid Sushi
    - 5 Egg Sushi
    - 10 Pudding
    - 6 Wasabi
    - 4 Chopsticks
    """
    
    # Cards per player based on player count
    CARDS_PER_PLAYER = {
        2: 10,
        3: 9,
        4: 8,
        5: 7
    }
    
    def __init__(self):
        self.cards: List[Card] = []
        self._create_deck()
        self.shuffle()
    
    def _create_deck(self):
        """Create the full 108-card deck"""
        self.cards = []
        
        # 14 Tempura
        for _ in range(14):
            self.cards.append(Card(CardType.TEMPURA))
        
        # 14 Sashimi
        for _ in range(14):
            self.cards.append(Card(CardType.SASHIMI))
        
        # 14 Dumpling
        for _ in range(14):
            self.cards.append(Card(CardType.DUMPLING))
        
        # Maki: 6x(1), 12x(2), 8x(3)
        for _ in range(6):
            self.cards.append(Card(CardType.MAKI, maki_count=1))
        for _ in range(12):
            self.cards.append(Card(CardType.MAKI, maki_count=2))
        for _ in range(8):
            self.cards.append(Card(CardType.MAKI, maki_count=3))
        
        # 10 Salmon Sushi
        for _ in range(10):
            self.cards.append(Card(CardType.SALMON))
        
        # 5 Squid Sushi
        for _ in range(5):
            self.cards.append(Card(CardType.SQUID))
        
        # 5 Egg Sushi
        for _ in range(5):
            self.cards.append(Card(CardType.EGG))
        
        # 10 Pudding
        for _ in range(10):
            self.cards.append(Card(CardType.PUDDING))
        
        # 6 Wasabi
        for _ in range(6):
            self.cards.append(Card(CardType.WASABI))
        
        # 4 Chopsticks
        for _ in range(4):
            self.cards.append(Card(CardType.CHOPSTICKS))
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def deal(self, num_players: int) -> List[List[Card]]:
        """
        Deal hands to players based on number of players, returns list of hands (list of cards per player)
        Remaining cards stay in self.cards but are not used in the round
        """

        num_cards = self.CARDS_PER_PLAYER.get(num_players, 7)
        
        hands = []
        for i in range(num_players):
            start = i * num_cards
            end = start + num_cards
            hands.append(self.cards[start:end])
        
        return hands
    
    def __len__(self) -> int:
        """Return the total number of cards in the deck."""
        return len(self.cards)
