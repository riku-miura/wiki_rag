import { writable } from 'svelte/store';

/**
 * @typedef {Object} RagSession
 * @property {string|null} sessionId
 * @property {'idle'|'loading'|'ready'|'error'} status
 * @property {string|null} error
 * @property {string|null} articleUrl
 * @property {number} progress
 */

/** @type {RagSession} */
const initialState = {
    sessionId: null,
    status: 'idle',
    error: null,
    articleUrl: null,
    progress: 0
};

function createSessionStore() {
    const { subscribe, set, update } = writable(initialState);

    return {
        subscribe,
        set,
        update,
        reset: () => set(initialState),
        setLoading: () => update(s => ({ ...s, status: 'loading', error: null, progress: 0 })),
        setStatus: (status) => update(s => ({ ...s, status })),
        setError: (error) => update(s => ({ ...s, status: 'error', error })),
        setSessionId: (id) => update(s => ({ ...s, sessionId: id })),
        setProgress: (progress) => update(s => ({ ...s, progress }))
    };
}

export const session = createSessionStore();
