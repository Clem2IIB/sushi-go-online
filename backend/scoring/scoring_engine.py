"""
Scoring engine for Sushi Go!
Implements all scoring rules per official rulebook
"""

from typing import Dict, List, Any

from models.cards import CardType
from models.player import Player


class ScoringEngine:
    """
    Handles all scoring logic per official Sushi Go! rules
    
    Scoring summary:
    - Maki: Most symbols = 6 pts, Second = 3 pts (split if tied)
    - Tempura: Pair = 5 pts
    - Sashimi: Set of 3 = 10 pts
    - Dumpling: 1/3/6/10/15 pts for 1/2/3/4/5+ cards
    - Salmon: 2 pts (6 with Wasabi)
    - Squid: 3 pts (9 with Wasabi)
    - Egg: 1 pt (3 with Wasabi)
    - Wasabi: Triples next sushi value
    - Chopsticks: 0 pts (utility card)
    - Pudding: End game - Most = +6, Least = -6
    """
    
    @staticmethod
    def score_maki(players: List[Player]) -> Dict[str, int]:
        """
        Score maki rolls - 6 points for most, 3 for second
        Points are split (rounded down) if tied
        """
        scores = {p.player_id: 0 for p in players}
        
        # Count maki symbols per player
        maki_counts = [
            (player.player_id, player.count_maki_symbols())
            for player in players
        ]
        
        # Check if anyone has maki
        if not maki_counts or max(c[1] for c in maki_counts) == 0:
            return scores
        
        # Sort by count descending
        maki_counts.sort(key=lambda x: x[1], reverse=True)
        
        # First place
        first_count = maki_counts[0][1]
        first_place = [pid for pid, count in maki_counts if count == first_count]
        
        if len(first_place) > 1:
            # Tie for first: split 6 points, no second place awarded
            points = 6 // len(first_place)
            for pid in first_place:
                scores[pid] = points
        else:
            # Clear first place: 6 points
            scores[first_place[0]] = 6
            
            # Find second place
            remaining = [
                (pid, count) for pid, count in maki_counts 
                if count < first_count and count > 0
            ]
            if remaining:
                second_count = remaining[0][1]
                second_place = [pid for pid, count in remaining if count == second_count]
                points = 3 // len(second_place)
                for pid in second_place:
                    scores[pid] = points
        
        return scores
    
    @staticmethod
    def score_tempura(player: Player) -> int:
        """
        Score tempura - pairs worth 5 points each
        Incomplete pairs worth nothing
        """
        count = player.count_card_type(CardType.TEMPURA)
        return (count // 2) * 5
    
    @staticmethod
    def score_sashimi(player: Player) -> int:
        """
        Score sashimi - sets of 3 worth 10 points each
        Incomplete sets worth nothing
        """
        count = player.count_card_type(CardType.SASHIMI)
        return (count // 3) * 10
    
    @staticmethod
    def score_dumpling(player: Player) -> int:
        """
        Score dumpling - progressive scoring
        1=1, 2=3, 3=6, 4=10, 5+=15
        """
        count = player.count_card_type(CardType.DUMPLING)
        scoring = {0: 0, 1: 1, 2: 3, 3: 6, 4: 10}
        return scoring.get(count, 15)
    
    @staticmethod
    def score_sushi(player: Player) -> int:
        """
        Score sushi cards (with wasabi multiplier)
        Salmon: 2 (6 with wasabi)
        Squid: 3 (9 with wasabi)
        Egg: 1 (3 with wasabi)
        """
        total = 0
        
        for card in player.played_cards:
            if card.is_sushi():
                value = card.get_base_value()
                if card.on_wasabi:
                    value *= 3
                total += value
        
        return total
    
    @staticmethod
    def score_round(players: List[Player]) -> Dict[str, Dict[str, Any]]:
        """
        Score all cards for a round
        
        Returns:
            Dictionary mapping player_id to score breakdown
        """
        results = {}
        
        # Maki scoring (comparative between all players)
        maki_scores = ScoringEngine.score_maki(players)
        
        for player in players:
            breakdown = {
                "maki": maki_scores.get(player.player_id, 0),
                "tempura": ScoringEngine.score_tempura(player),
                "sashimi": ScoringEngine.score_sashimi(player),
                "dumpling": ScoringEngine.score_dumpling(player),
                "sushi": ScoringEngine.score_sushi(player)
            }
            breakdown["total"] = sum(breakdown.values())
            results[player.player_id] = breakdown
        
        return results
    
    @staticmethod
    def score_pudding(players: List[Player], is_two_player: bool = False) -> Dict[str, int]:
        """
        Score pudding at end of game
        Most pudding: +6 points (split if tied)
        Least pudding: -6 points (split if tied, not in 2-player)
        
        Args:
            players: List of all players
            is_two_player: If True, no penalty for least pudding
        """
        scores = {p.player_id: 0 for p in players}
        
        pudding_counts = [
            (p.player_id, len(p.pudding_cards)) 
            for p in players
        ]
        
        if not pudding_counts:
            return scores
        
        counts = [c[1] for c in pudding_counts]
        
        # Check if all tied (no points awarded)
        if len(set(counts)) == 1:
            return scores
        
        # Most pudding: +6
        max_count = max(counts)
        most = [pid for pid, count in pudding_counts if count == max_count]
        points = 6 // len(most)
        for pid in most:
            scores[pid] = points
        
        # Least pudding: -6 (not in 2-player game)
        if not is_two_player:
            min_count = min(counts)
            least = [
                pid for pid, count in pudding_counts 
                if count == min_count and pid not in most
            ]
            if least:
                penalty = -6 // len(least)
                for pid in least:
                    scores[pid] = penalty
        
        return scores
    
    @staticmethod
    def apply_round_scores(players: List[Player], scores: Dict[str, Dict[str, Any]], 
                          current_round: int):
        """
        Apply round scores to players
        
        Args:
            players: List of players
            scores: Score breakdown from score_round()
            current_round: Current round number (1-3)
        """
        for player in players:
            if player.player_id in scores:
                round_score = scores[player.player_id]["total"]
                player.round_scores[current_round - 1] = round_score
                player.score += round_score
    
    @staticmethod
    def apply_pudding_scores(players: List[Player], scores: Dict[str, int]):
        """Apply pudding scores to players"""
        for player in players:
            if player.player_id in scores:
                player.score += scores[player.player_id]
    
    @staticmethod
    def get_rankings(players: List[Player]) -> List[Dict[str, Any]]:
        """
        Get final rankings
        Tiebreaker: most pudding cards
        """
        ranked = sorted(
            players,
            key=lambda p: (p.score, len(p.pudding_cards)),
            reverse=True
        )
        
        return [
            {
                "rank": i + 1,
                "player_id": p.player_id,
                "name": p.name,
                "score": p.score,
                "pudding": len(p.pudding_cards),
                "round_scores": p.round_scores
            }
            for i, p in enumerate(ranked)
        ]
