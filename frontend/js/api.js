/**
 * Sushi Go! - API Module
 * Handles HTTP API communication
 */

const API = {
    BASE_URL: '',
    
    /**
     * Create a new game
     * @param {string} hostName - Name of the host player
     * @returns {Promise<Object>} Result with game_code, player_id
     */
    async createGame(hostName) {
        try {
            const response = await fetch(`${this.BASE_URL}/api/create-game`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name: hostName })
            });
            
            const data = await response.json();
            return data;
        } catch (err) {
            console.error('Create game error:', err);
            return { success: false, error: 'Connection error' };
        }
    },
    
    /**
     * Join an existing game
     * @param {string} gameCode - The game code to join
     * @param {string} playerName - Name of the joining player
     * @returns {Promise<Object>} Result with player_id
     */
    async joinGame(gameCode, playerName) {
        try {
            const response = await fetch(`${this.BASE_URL}/api/join-game`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ game_code: gameCode, name: playerName })
            });
            
            if (!response.ok) {
                const err = await response.json();
                return { success: false, error: err.detail };
            }
            
            const data = await response.json();
            return data;
        } catch (err) {
            console.error('Join game error:', err);
            return { success: false, error: 'Connection error' };
        }
    },
    
    /**
     * Get game information
     * @param {string} gameCode - The game code
     * @returns {Promise<Object>} Game state
     */
    async getGameInfo(gameCode) {
        try {
            const response = await fetch(`${this.BASE_URL}/api/game/${gameCode}`);
            
            if (!response.ok) {
                return null;
            }
            
            return await response.json();
        } catch (err) {
            console.error('Get game info error:', err);
            return null;
        }
    }
};
