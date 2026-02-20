/**
 * Sushi Go! - UI Module
 * Handles all UI rendering and DOM manipulation
 */
const CARD_INFO = {
    maki: {
        title: "Maki Rolls",
        scoring: "Most symbols → 6 pts | Second most → 3 pts | Ties split (rounded down)",
        description: "Each card shows 1, 2, or 3 maki symbols. At round end, count your total symbols and compare with other players.",
        tip: "Look at the number of rolls on the card! Aim for majority or don't bother."
    },
    tempura: {
        title: "Tempura",
        scoring: "2 cards → 5 pts | 4 cards → 10 pts | 1 or 3 cards → wasted",
        description: "Only scores in complete pairs. Odd tempura at round end scores nothing.",
        tip: "Commit to pairs or skip entirely. One tempura is worthless!"
    },
    sashimi: {
        title: "Sashimi",
        scoring: "3 cards → 10 pts | 6 cards → 20 pts | 1-2 cards → wasted",
        description: "Only scores in complete sets of three. Very hard to collect but high reward.",
        tip: "Risky! Only go for sashimi if you see multiple early."
    },
    dumpling: {
        title: "Dumpling",
        scoring: "1→1 | 2→3 | 3→6 | 4→10 | 5+→15 pts",
        description: "Each additional dumpling increases total value. No incomplete sets, every dumpling counts!",
        tip: "Safest card! Even 1 gives a point, and 5+ maxes at 15."
    },
    salmon: {
        title: "Salmon Sushi",
        scoring: "Base: 2 pts | On wasabi: 2 × 3 = 6 pts",
        description: "If you have an unused wasabi card, this sushi automatically goes on it for triple points.",
        tip: "Solid value! Good wasabi target if squid isn't available."
    },
    squid: {
        title: "Squid Sushi",
        scoring: "Base: 3 pts | On wasabi: 3 × 3 = 9 pts",
        description: "Highest-value sushi. If you have an unused wasabi card, this automatically goes on it.",
        tip: "Best wasabi combo! Prioritize squid if you have wasabi waiting."
    },
    egg: {
        title: "Egg Sushi",
        scoring: "Base: 1 pt | On wasabi: 1 × 3 = 3 pts",
        description: "Lowest-value sushi. If you have an unused wasabi card, this automatically goes on it.",
        tip: "Weak card. Avoid playing wasabi if only egg is coming!"
    },
    wasabi: {
        title: "Wasabi",
        scoring: "Wasabi + Squid = 9 pts | + Salmon = 6 pts | + Egg = 3 pts | Alone = 0 pts",
        description: "Play wasabi BEFORE a sushi card. Your next sushi will get automaticallytripled (salmon/squid/egg).",
        tip: "Play early when you expect good sushi coming. Empty wasabi = 0 pts!"
    },
    chopsticks: {
        title: "Chopsticks",
        scoring: "Worth 0 pts - utility only",
        description: "On a future turn, select TWO cards instead of one. The chopsticks then goes back into the passing hand.",
        tip: "Play 2 cards in one turn! Great for grabbing two key cards at once (sashimi, tempura, etc.)"
    },
    pudding: {
        title: "Pudding",
        scoring: "At end game: Most puddings → +6 pts | Fewest → -6 pts | All tied → no points",
        description: "Collected across ALL 3 rounds. Only scored at game end. In 2-player: no penalty for least.",
        tip: "Don't ignore! The -6 penalty often decides close games."
    }
};

function showCardTooltip(card, event) {
    const tooltip = document.getElementById('card-tooltip');
    const cardType = card.type.replace('_sushi', '').replace('_', '');
    const info = CARD_INFO[cardType] || CARD_INFO[card.type];
    
    if (!info) return;
    
    tooltip.querySelector('.tooltip-image').src = `/static/assets/cards/${card.image}`;
    tooltip.querySelector('.tooltip-title').textContent = info.title;
    tooltip.querySelector('.tooltip-scoring').textContent = info.scoring;
    tooltip.querySelector('.tooltip-description').textContent = info.description;
    tooltip.querySelector('.tooltip-tip').textContent = "💡 " + info.tip;
    
    // Position tooltip
    const x = event.clientX + 20;
    const y = event.clientY - 100;
    
    // Keep on screen
    const maxX = window.innerWidth - 300;
    const maxY = window.innerHeight - 250;
    
    tooltip.style.left = Math.min(x, maxX) + 'px';
    tooltip.style.top = Math.max(10, Math.min(y, maxY)) + 'px';
    tooltip.classList.add('visible');
}

function hideCardTooltip() {
    document.getElementById('card-tooltip').classList.remove('visible');
}

const CARD_SORT_ORDER = {
    'maki': 1,
    'tempura': 2,
    'sashimi': 3,
    'dumpling': 4,
    'wasabi': 5,
    'salmon': 6,
    'squid': 7,
    'egg': 8,
    'chopsticks': 9
};

function sortCardsByCategory(cards) {
    return [...cards].sort((a, b) => {
        const orderA = CARD_SORT_ORDER[a.type] || 99;
        const orderB = CARD_SORT_ORDER[b.type] || 99;
        return orderA - orderB;
    });
}

const UI = {
    /**
     * Create a card DOM element
     * @param {Object} card - Card data
     * @param {boolean} isSmall - Whether to use small card size
     * @returns {HTMLElement} Card element
     */
    createCardElement(card, isSmall = false) {
        const cardEl = document.createElement('div');
        cardEl.className = `card ${isSmall ? 'card-small' : ''}`;
        cardEl.dataset.cardId = card.id;
    
        if (card.on_wasabi) {
            cardEl.classList.add('on-wasabi');
        }
    
        // Store card data for tooltip
        cardEl.cardData = card;
    
        // Add hover events for tooltip (not on small cards)
        cardEl.addEventListener('mouseenter', (e) => showCardTooltip(card, e));
        cardEl.addEventListener('mousemove', (e) => showCardTooltip(card, e));
        cardEl.addEventListener('mouseleave', hideCardTooltip);
        
    
    // Create image
    const img = document.createElement('img');
    img.src = `/static/assets/cards/${card.image}`;
    img.alt = card.display_name;
    
        img.onerror = () => {
            cardEl.classList.add('placeholder');
            cardEl.innerHTML = `<span>${card.display_name}</span>`;
        };
        
        cardEl.appendChild(img);
    
        if (isSmall) {
            const label = document.createElement('div');
            label.className = 'card-label';
            label.textContent = card.display_name;
            cardEl.appendChild(label);
        }
        
        return cardEl;
    },
    
    /**
     * Render cards into a container
     * @param {HTMLElement} container - Container element
     * @param {Array} cards - Array of card data
     * @param {boolean} isSmall - Whether to use small card size
     */
    renderCards(container, cards, isSmall = false) {
        container.innerHTML = '';
        
        // Sort cards by category before rendering
        const sortedCards = sortCardsByCategory(cards);
        
        sortedCards.forEach(card => {
            const cardEl = this.createCardElement(card, isSmall);
            container.appendChild(cardEl);
        });
    },
    
    /**
     * Render opponent boards
     * @param {HTMLElement} container - Container element
     * @param {Array} opponents - Array of opponent player data
     * @param {string} currentPlayerId - Current player's ID
     */
    renderOpponents(container, opponents, currentPlayerId) {
        container.innerHTML = '';
        
        opponents.forEach(opponent => {
            if (opponent.player_id === currentPlayerId) return;
            
            const board = document.createElement('div');
            board.className = 'opponent-board';
            
            board.innerHTML = `
                <h4>
                    <span>${opponent.name}</span>
                    <span>${opponent.score} pts | 🍰${opponent.pudding_count}</span>
                </h4>
                <div class="opponent-cards"></div>
            `;
            
            const cardsContainer = board.querySelector('.opponent-cards');
            
            // Sort opponent cards by category
            const sortedCards = sortCardsByCategory(opponent.played_cards);
            
            sortedCards.forEach(card => {
                const cardEl = this.createCardElement(card, true);
                cardsContainer.appendChild(cardEl);
            });
            
            container.appendChild(board);
        });
    },
    
    /**
     * Show reveal overlay with played cards
     * @param {Object} revealData - Data for each player's revealed cards
     * @param {Array} players - Player data array
     * @param {string} currentPlayerId - Current player's ID
     */
    showRevealOverlay(revealData, players, currentPlayerId) {
        const overlay = document.getElementById('reveal-overlay');
        const container = document.getElementById('revealed-cards');
        container.innerHTML = '';
        
        for (const [playerId, info] of Object.entries(revealData)) {
            const player = players.find(p => p.player_id === playerId);
            if (!player) continue;
            
            const div = document.createElement('div');
            div.className = 'reveal-player';
            
            let cardsHtml = '<div class="reveal-cards">';
            info.cards_played.forEach(card => {
                cardsHtml += `
                    <div class="card card-small">
                        <img src="/static/assets/cards/${card.image}" 
                             alt="${card.display_name}"
                             onerror="this.parentElement.classList.add('placeholder'); this.parentElement.innerHTML='<span>${card.display_name}</span>'">
                    </div>
                `;
            });
            cardsHtml += '</div>';
            
            const isMe = player.player_id === currentPlayerId;
            div.innerHTML = `
                <h4>${player.name}${isMe ? ' (You)' : ''}</h4>
                ${cardsHtml}
                ${info.used_chopsticks ? '<p>🥢 Used Chopsticks!</p>' : ''}
            `;
            
            container.appendChild(div);
        }
        
        overlay.classList.remove('hidden');
        
        // Auto-hide after delay
        setTimeout(() => {
            overlay.classList.add('hidden');
        }, 2500);
    },
    
    /**
     * Show round end overlay with scores
     * @param {Object} data - Round end data with scores
     * @param {Array} players - Player data array
     * @param {string} currentPlayerId - Current player's ID
     * @param {boolean} isHost - Whether current player is host
     */
    showRoundEndOverlay(data, players, currentPlayerId, isHost) {
        const overlay = document.getElementById('round-end-overlay');
        const scoresContainer = document.getElementById('round-scores');
        
        document.getElementById('ended-round').textContent = data.round;
        scoresContainer.innerHTML = '';
        
        // Sort by round score
        const sortedPlayers = [...players].sort((a, b) => {
            const scoreA = data.scores[a.player_id]?.total || 0;
            const scoreB = data.scores[b.player_id]?.total || 0;
            return scoreB - scoreA;
        });
        
        sortedPlayers.forEach(player => {
            const scores = data.scores[player.player_id] || {};
            const isMe = player.player_id === currentPlayerId;
            
            const row = document.createElement('div');
            row.className = `score-row ${isMe ? 'highlight' : ''}`;
            
            row.innerHTML = `
                <div>
                    <strong>${player.name}${isMe ? ' (You)' : ''}</strong>
                    <div class="score-breakdown">
                        Maki: ${scores.maki || 0} | 
                        Tempura: ${scores.tempura || 0} | 
                        Sashimi: ${scores.sashimi || 0} | 
                        Dumpling: ${scores.dumpling || 0} | 
                        Sushi: ${scores.sushi || 0}
                    </div>
                </div>
                <div class="score-total">+${scores.total || 0}</div>
            `;
            
            scoresContainer.appendChild(row);
        });
        
        // Show/hide next round button
        const nextRoundBtn = document.getElementById('next-round-btn');
        const waitingHost = document.getElementById('waiting-host');
        
        if (isHost && data.round < 3) {
            nextRoundBtn.classList.remove('hidden');
            document.getElementById('next-round-num').textContent = data.round + 1;
            waitingHost.classList.add('hidden');
        } else if (data.round >= 3) {
            nextRoundBtn.classList.add('hidden');
            waitingHost.textContent = 'Calculating final scores...';
            waitingHost.classList.remove('hidden');
        } else {
            nextRoundBtn.classList.add('hidden');
            waitingHost.classList.remove('hidden');
            waitingHost.textContent = 'Waiting for host to continue...';
        }
        
        overlay.classList.remove('hidden');
    },
    
    /**
     * Show game end overlay with final scores
     * @param {Object} data - Game end data with rankings
     * @param {string} currentPlayerId - Current player's ID
     */
    showGameEndOverlay(data, currentPlayerId) {
        const overlay = document.getElementById('game-end-overlay');
        const scoresContainer = document.getElementById('final-scores');
        
        // Hide round end overlay if showing
        document.getElementById('round-end-overlay').classList.add('hidden');
        
        scoresContainer.innerHTML = '';
        
        data.rankings.forEach((player, index) => {
            const isMe = player.player_id === currentPlayerId;
            const puddingScore = data.pudding_scores[player.player_id] || 0;
            
            const row = document.createElement('div');
            row.className = `score-row ${isMe ? 'highlight' : ''}`;
            
            row.innerHTML = `
                <div>
                    <strong>${index === 0 ? '🏆 ' : ''}#${player.rank} ${player.name}${isMe ? ' (You)' : ''}</strong>
                    <div class="score-breakdown">
                        Rounds: ${player.round_scores.join(' + ')} | 
                        Pudding: ${puddingScore > 0 ? '+' : ''}${puddingScore} (${player.pudding} 🍰)
                    </div>
                </div>
                <div class="score-total">${player.score} pts</div>
            `;
            
            scoresContainer.appendChild(row);
        });
        
        document.getElementById('winner-announcement').textContent = `🎉 ${data.winner} wins! 🎉`;
        
        overlay.classList.remove('hidden');
    },
    
    /**
     * Hide all overlays
     */
    hideOverlays() {
        document.getElementById('reveal-overlay').classList.add('hidden');
        document.getElementById('round-end-overlay').classList.add('hidden');
        document.getElementById('game-end-overlay').classList.add('hidden');
    }
};
