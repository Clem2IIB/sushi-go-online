/**
 * Sushi Go! - Lobby Module
 * Handles pre-game lobby functionality
 */

class Lobby {
    constructor() {
        this.playerId = sessionStorage.getItem('player_id');
        this.gameCode = sessionStorage.getItem('game_code');
        this.playerName = sessionStorage.getItem('player_name');
        this.isHost = sessionStorage.getItem('is_host') === 'true';
        this.gameState = null;
        this.ws = null;
        
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
        this.lobbyCode = document.getElementById('lobby-code');
        this.lobbyPlayers = document.getElementById('lobby-players');
        this.playerCount = document.getElementById('player-count');
        this.startGameBtn = document.getElementById('start-game-btn');
        this.startHint = document.getElementById('start-hint');
        this.lobbyStatus = document.getElementById('lobby-status');
        
        // Set game code
        this.lobbyCode.textContent = this.gameCode;
    }
    
    connectWebSocket() {
        this.ws = new GameWebSocket(this.gameCode, this.playerId);
        
        this.ws.on('game_state', (msg) => this.handleGameState(msg.data));
        this.ws.on('player_connected', (msg) => this.handlePlayerConnected(msg));
        this.ws.on('player_disconnected', (msg) => this.handlePlayerDisconnected(msg));
        this.ws.on('game_started', () => this.handleGameStarted());
        this.ws.on('error', (msg) => this.handleError(msg));
        
        this.ws.connect();
    }
    
    bindEvents() {
        // Start game button
        this.startGameBtn.addEventListener('click', () => {
            this.ws.send({ action: 'start_game' });
        });
        
        // Copy code button
        document.getElementById('copy-code-btn').addEventListener('click', () => {
            this.copyGameCode();
        });
    }
    
    handleGameState(state) {
        this.gameState = state;
        
        // If game started, redirect to game page
        if (state.phase !== 'lobby') {
            window.location.href = `/game/${this.gameCode}`;
            return;
        }
        
        this.updatePlayerList();
        this.updateStartButton();
    }
    
    handlePlayerConnected(msg) {
        this.lobbyStatus.textContent = `${msg.name} joined the game!`;
    }
    
    handlePlayerDisconnected(msg) {
        this.lobbyStatus.textContent = 'A player disconnected';
    }
    
    handleGameStarted() {
        window.location.href = `/game/${this.gameCode}`;
    }
    
    handleError(msg) {
        if (msg && msg.message) {
            alert(msg.message);
        }
    }
    
    updatePlayerList() {
        if (!this.gameState) return;
        
        this.lobbyPlayers.innerHTML = '';
        
        this.gameState.players.forEach(player => {
            const li = document.createElement('li');
            li.textContent = player.name;
            
            if (player.player_id === this.gameState.host_id) {
                li.classList.add('host');
            }
            if (!player.is_connected) {
                li.classList.add('disconnected');
            }
            if (player.player_id === this.playerId) {
                li.textContent += ' (You)';
            }
            
            this.lobbyPlayers.appendChild(li);
        });
        
        this.playerCount.textContent = `(${this.gameState.player_count}/5)`;
    }
    
    updateStartButton() {
        if (!this.gameState) return;
        
        const canStart = this.gameState.player_count >= 2;
        
        if (this.isHost) {
            this.startGameBtn.style.display = 'block';
            this.startGameBtn.disabled = !canStart;
            this.startHint.textContent = canStart 
                ? 'Ready to start!' 
                : 'Need at least 2 players';
        } else {
            this.startGameBtn.style.display = 'none';
            this.startHint.textContent = 'Waiting for host to start...';
        }
    }
    
    copyGameCode() {
        navigator.clipboard.writeText(this.gameCode).then(() => {
            alert('Game code copied!');
        }).catch(() => {
            // Fallback
            const input = document.createElement('input');
            input.value = this.gameCode;
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
            alert('Game code copied!');
        });
    }
}

// Initialize lobby when page loads
document.addEventListener('DOMContentLoaded', () => {
    new Lobby();
});
