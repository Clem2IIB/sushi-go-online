"""
Sushi Go! V2 - Card Models
This module defines the Card dataclass and CardType enum used throughout the backend files.
Adds dictionary method for JSON serialization and utility methods for card properties

This card class is kept simple to simply hold data about the card, the game logic like scoring, wasabi etc. is handled in other modules.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CardType(Enum):
    """All card types in Sushi Go, using an enum for type safety and clarity, over simple strings"""
    MAKI = "maki"
    TEMPURA = "tempura"
    SASHIMI = "sashimi"
    DUMPLING = "dumpling"
    SALMON = "salmon"
    SQUID = "squid"
    EGG = "egg"
    WASABI = "wasabi"
    CHOPSTICKS = "chopsticks"
    PUDDING = "pudding"


@dataclass
class Card:
    """
    Represents a single card in the game, giving the card type, unique ID, and its properties like maki count and placed on wasabi
    It is used for the frontend to identify specific cards and their properties, because without unique IDs, 2 cards would be the same in the JSON
    """
    card_type: CardType
    id: str = ""
    maki_count: int = 0  # For maki cards: 1, 2, or 3
    on_wasabi: bool = False  # For sushi cards placed on wasabi
    
    def __post_init__(self):
        """Generate a unique ID if not provided"""
        if not self.id:
            self.id = f"{self.card_type.value}_{random.randint(1000, 9999)}"
    
    def to_dict(self) -> dict:
        """Convert card to dictionary for JSON serialization for Websocket transmission"""
        return {
            "id": self.id,
            "type": self.card_type.value,
            "maki_count": self.maki_count,
            "on_wasabi": self.on_wasabi,
            "display_name": self.get_display_name(),
            "image": self.get_image_name()
        }
    
    def get_display_name(self) -> str:
        """Get human-readable card name"""
        names = {
            CardType.MAKI: f"Maki ({self.maki_count})",
            CardType.TEMPURA: "Tempura",
            CardType.SASHIMI: "Sashimi",
            CardType.DUMPLING: "Dumpling",
            CardType.SALMON: "Salmon Sushi",
            CardType.SQUID: "Squid Sushi",
            CardType.EGG: "Egg Sushi",
            CardType.WASABI: "Wasabi",
            CardType.CHOPSTICKS: "Chopsticks",
            CardType.PUDDING: "Pudding"
        }
        return names.get(self.card_type, self.card_type.value)
    
    def get_image_name(self) -> str:
        """Get image filename for this card"""
        if self.card_type == CardType.MAKI:
            return f"maki_{self.maki_count}.png"
        
        images = {
            CardType.TEMPURA: "tempura.png",
            CardType.SASHIMI: "sashimi.png",
            CardType.DUMPLING: "dumpling.png",
            CardType.SALMON: "salmon_sushi.png",
            CardType.SQUID: "squid_sushi.png",
            CardType.EGG: "egg_sushi.png",
            CardType.WASABI: "wasabi.png",
            CardType.CHOPSTICKS: "chopsticks.png",
            CardType.PUDDING: "pudding.png"
        }
        return images.get(self.card_type, "placeholder.png")
    
    def is_sushi(self) -> bool:
        """Check if the card is a sushi card that can be placed on wasabi"""
        return self.card_type in [CardType.SALMON, CardType.SQUID, CardType.EGG]
    
    def get_base_value(self) -> int:
        """Get base point value for sushi cards"""
        values = {
            CardType.SALMON: 2,
            CardType.SQUID: 3,
            CardType.EGG: 1
        }
        return values.get(self.card_type, 0)
