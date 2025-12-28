import { writable } from 'svelte/store';
import { apiClient } from '../services/api_client';

function createChatStore() {
    const { subscribe, update, set } = writable({
        sessionId: null,
        messages: [],
        isLoading: false,
        error: null,
        ragStatus: 'idle' // idle, building, ready, error
    });

    return {
        subscribe,

        setSessionId: (id) => update(s => ({ ...s, sessionId: id })),

        addMessage: (role, content) => update(s => ({
            ...s,
            messages: [...s.messages, { role, content, timestamp: new Date() }]
        })),

        async buildRag(url) {
            update(s => ({ ...s, isLoading: true, error: null, ragStatus: 'building' }));
            try {
                const data = await apiClient.buildRag(url);
                // In a real app, we'd poll status. For now, assume 'processing' needs polling
                // or if sync (Phase 1 simplicity), it might return ready.
                // The backend implementation of build_rag_session returns the session object.

                update(s => ({
                    ...s,
                    sessionId: data.session_id,
                    ragStatus: data.status, // processing or ready
                    isLoading: false
                }));
                return data;
            } catch (err) {
                update(s => ({
                    ...s,
                    isLoading: false,
                    error: err.message,
                    ragStatus: 'error'
                }));
                throw err;
            }
        },

        async sendQuery(queryText) {
            update(s => ({
                ...s,
                isLoading: true,
                messages: [...s.messages, { role: 'user', content: queryText, timestamp: new Date() }]
            }));

            try {
                // Get current state for session ID
                let currentState;
                subscribe(val => currentState = val)();

                if (!currentState.sessionId) throw new Error("No active session");

                const data = await apiClient.chatQuery(currentState.sessionId, queryText);

                update(s => ({
                    ...s,
                    isLoading: false,
                    messages: [...s.messages, { role: 'assistant', content: data.response, timestamp: new Date() }]
                }));
            } catch (err) {
                update(s => ({
                    ...s,
                    isLoading: false,
                    messages: [...s.messages, { role: 'system', content: `Error: ${err.message}`, isError: true }]
                }));
            }
        },

        reset: () => set({ sessionId: null, messages: [], isLoading: false, error: null, ragStatus: 'idle' })
    };
}

export const chatStore = createChatStore();
