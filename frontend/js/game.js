/**
 * Sushi Go! - Game Module
 * Main game controller
 */

class Game {
    constructor() {
        this.playerId = sessionStorage.getItem('player_id');
        this.gameCode = sessionStorage.getItem('game_code');
        this.playerName = sessionStorage.getItem('player_name');
        this.isHost = sessionStorage.getItem('is_host') === 'true';
        
        this.gameState = null;
        this.ws = null;
        this.selectedCard = null;
        this.secondSelectedCard = null;
        this.usingChopsticks = false;
        
        // Verify credentials
        if (!this.playerId || !this.gameCode) {
            window.location.href = '/';
            return;
        }
        
        this.initElements();
        this.connectWebSocket();
        this.bindEvents();
    }
    
    initElements() {
        // Game info
        this.roundDisplay = document.getElementById('round-display');
        this.turnDisplay = document.getElementById('turn-display');
        this.directionDisplay = document.getElementById('direction-display');
        
        // Card areas
        this.opponentsContainer = document.getElementById('opponents-container');
        this.yourPlayedCards = document.getElementById('your-played-cards');
        this.yourPudding = document.getElementById('your-pudding').querySelector('span');
        this.yourHand = document.getElementById('your-hand');
        this.handCount = document.getElementById('hand-count');
        this.yourScore = document.getElementById('your-score');
        
        // Action area
        this.selectionInfo = document.getElementById('selection-info');
        this.chopsticksPrompt = document.getElementById('chopsticks-prompt');
        this.confirmBtn = document.getElementById('confirm-selection');
        this.waitingIndicator = document.getElementById('waiting-indicator');
        this.readyCount = document.getElementById('ready-count');
    }
    
    connectWebSocket() {
        this.ws = new GameWebSocket(this.gameCode, this.playerId);
        
        this.ws.on('game_state', (msg) => this.handleGameState(msg.data));
        this.ws.on('player_ready', (msg) => this.handlePlayerReady(msg));
        this.ws.on('cards_revealed', (msg) => this.handleCardsRevealed(msg.data));
        this.ws.on('round_end', (msg) => this.handleRoundEnd(msg.data));
        this.ws.on('game_end', (msg) => this.handleGameEnd(msg.data));
        this.ws.on('new_round', (msg) => this.handleNewRound(msg.data));
        this.ws.on('error', (msg) => this.handleError(msg));
        
        this.ws.connect();
    }
    
    bindEvents() {
        // Confirm selection button
        this.confirmBtn.addEventListener('click', () => {
            this.confirmSelection();
        });
        
        // Skip chopsticks button
        document.getElementById('skip-chopsticks').addEventListener('click', () => {
            this.usingChopsticks = false;
            this.secondSelectedCard = null;
            this.chopsticksPrompt.classList.add('hidden');
            this.confirmSelection();
        });
        
        // Next round button
        document.getElementById('next-round-btn').addEventListener('click', () => {
            this.ws.send({ action: 'next_round' });
        });
    }
    
    handleGameState(state) {
        this.gameState = state;
        
        // Redirect to lobby if game not started
        if (state.phase === 'lobby') {
            window.location.href = `/lobby/${this.gameCode}`;
            return;
        }
        
        this.updateGameDisplay();
    }
    
    handlePlayerReady(msg) {
        const readyPlayers = this.gameState.players.filter(p => p.is_ready).length + 1;
        this.readyCount.textContent = `(${readyPlayers}/${this.gameState.player_count})`;
    }
    
    handleCardsRevealed(data) {
        UI.showRevealOverlay(data, this.gameState.players, this.playerId);
    }
    
    handleRoundEnd(data) {
        UI.showRoundEndOverlay(data, this.gameState.players, this.playerId, this.isHost);
    }
    
    handleGameEnd(data) {
        UI.showGameEndOverlay(data, this.playerId);
    }
    
    handleNewRound(data) {
        UI.hideOverlays();
    }
    
    handleError(msg) {
        if (msg && msg.message) {
            alert(msg.message);
        }
    }
    
    updateGameDisplay() {
        const state = this.gameState;
        
        // Update header
        this.roundDisplay.textContent = `Round ${state.current_round}/3`;
        this.turnDisplay.textContent = `Turn ${state.current_turn}`;
        this.directionDisplay.textContent = `Pass: ${state.pass_direction === 'left' ? '←' : '→'}`;
        
        // Find current player data
        const myData = state.players.find(p => p.player_id === this.playerId);
        if (!myData) return;
        
        // Update your score
        this.yourScore.textContent = `(${myData.score} pts)`;
        
        // Update your played cards
        UI.renderCards(this.yourPlayedCards, myData.played_cards, true);
        
        // Update pudding count
        this.yourPudding.textContent = myData.pudding_count;
        
        // Update your hand
        if (myData.hand) {
            this.handCount.textContent = `(${myData.hand.length} cards)`;
            this.renderHand(myData.hand, myData.has_chopsticks);
        }
        
        // Update opponents
        const opponents = state.players.filter(p => p.player_id !== this.playerId);
        UI.renderOpponents(this.opponentsContainer, opponents, this.playerId);
        
        // Reset selection UI for new turn
        this.resetSelectionUI();
    }
    
    renderHand(hand, hasChopsticks) {
        this.yourHand.innerHTML = '';
        
        hand.forEach(card => {
            const cardEl = UI.createCardElement(card, false);
            cardEl.addEventListener('click', () => this.selectCard(card, cardEl, hasChopsticks));
            this.yourHand.appendChild(cardEl);
        });
    }
    
    selectCard(card, cardEl, hasChopsticks) {
        // If already confirmed, don't allow changes
        if (!this.waitingIndicator.classList.contains('hidden')) {
            return;
        }
        
        // Handle chopsticks second selection
        if (this.usingChopsticks && this.selectedCard) {
            if (card.id === this.selectedCard.id) {
                // Clicking same card - deselect all
                this.selectedCard = null;
                this.secondSelectedCard = null;
                this.usingChopsticks = false;
                this.updateHandSelection();
                this.chopsticksPrompt.classList.add('hidden');
                return;
            }
            
            // Select second card
            this.secondSelectedCard = card;
            this.updateHandSelection();
            this.confirmBtn.disabled = false;
            return;
        }
        
        // Normal selection
        if (this.selectedCard && this.selectedCard.id === card.id) {
            // Deselect
            this.selectedCard = null;
            this.usingChopsticks = false;
            this.secondSelectedCard = null;
            this.chopsticksPrompt.classList.add('hidden');
        } else {
            this.selectedCard = card;
            this.secondSelectedCard = null;
            
            // Check for chopsticks opportunity
            const myData = this.gameState.players.find(p => p.player_id === this.playerId);
            if (hasChopsticks && myData && myData.hand.length > 1) {
                this.chopsticksPrompt.classList.remove('hidden');
                this.usingChopsticks = true;
            } else {
                this.chopsticksPrompt.classList.add('hidden');
                this.usingChopsticks = false;
            }
        }
        
        this.updateHandSelection();
    }
    
    updateHandSelection() {
        // Update visual selection
        const cards = this.yourHand.querySelectorAll('.card');
        cards.forEach(cardEl => {
            cardEl.classList.remove('selected', 'second-selected');
            
            if (this.selectedCard && cardEl.dataset.cardId === this.selectedCard.id) {
                cardEl.classList.add('selected');
            }
            if (this.secondSelectedCard && cardEl.dataset.cardId === this.secondSelectedCard.id) {
                cardEl.classList.add('second-selected');
            }
        });
        
        // Update confirm button and info
        if (this.usingChopsticks) {
            this.confirmBtn.disabled = !this.selectedCard || !this.secondSelectedCard;
            this.selectionInfo.innerHTML = this.secondSelectedCard 
                ? `<p>Playing: ${this.selectedCard.display_name} + ${this.secondSelectedCard.display_name}</p>`
                : `<p>Select a second card (Chopsticks)</p>`;
        } else {
            this.confirmBtn.disabled = !this.selectedCard;
            this.selectionInfo.innerHTML = this.selectedCard 
                ? `<p>Playing: ${this.selectedCard.display_name}</p>`
                : `<p>Select a card to play</p>`;
        }
    }
    
    confirmSelection() {
        if (!this.selectedCard) return;
        
        const message = {
            action: 'select_card',
            card_id: this.selectedCard.id,
            use_chopsticks: this.usingChopsticks && this.secondSelectedCard != null,
            second_card_id: this.secondSelectedCard ? this.secondSelectedCard.id : null
        };
        
        this.ws.send(message);
        
        // Show waiting state
        this.confirmBtn.classList.add('hidden');
        this.chopsticksPrompt.classList.add('hidden');
        this.waitingIndicator.classList.remove('hidden');
        this.readyCount.textContent = `(1/${this.gameState.player_count})`;
        
        // Disable hand interaction
        const cards = this.yourHand.querySelectorAll('.card');
        cards.forEach(c => c.style.pointerEvents = 'none');
    }
    
    resetSelectionUI() {
        this.selectedCard = null;
        this.secondSelectedCard = null;
        this.usingChopsticks = false;
        
        this.confirmBtn.classList.remove('hidden');
        this.confirmBtn.disabled = true;
        this.waitingIndicator.classList.add('hidden');
        this.chopsticksPrompt.classList.add('hidden');
        this.selectionInfo.innerHTML = '<p>Select a card to play</p>';
        
        // Enable hand interaction
        const cards = this.yourHand.querySelectorAll('.card');
        cards.forEach(c => c.style.pointerEvents = 'auto');
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    new Game();
});
