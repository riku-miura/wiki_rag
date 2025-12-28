const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000'; // Default to local for dev

export const apiClient = {
    async buildRag(url) {
        const response = await fetch(`${API_BASE_URL}/rag/build`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        if (!response.ok) throw new Error('Failed to start RAG build');
        return await response.json();
    },

    async checkStatus(sessionId) {
        const response = await fetch(`${API_BASE_URL}/rag/${sessionId}/status`);
        if (!response.ok) throw new Error('Failed to check status');
        return await response.json();
    },

    async chatQuery(sessionId, query) {
        const response = await fetch(`${API_BASE_URL}/chat/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, query })
        });
        if (!response.ok) throw new Error('Failed to send query');
        return await response.json();
    },

    async getHistory(sessionId) {
        const response = await fetch(`${API_BASE_URL}/chat/${sessionId}/history`);
        if (!response.ok) throw new Error('Failed to fetch history');
        return await response.json();
    }
};
