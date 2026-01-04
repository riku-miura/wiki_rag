export default class SSEHandler {
    constructor(callbacks) {
        this.onMessage = callbacks.onMessage || (() => { });
        this.onError = callbacks.onError || (() => { });
        this.onComplete = callbacks.onComplete || (() => { });
        this.controller = null;
    }

    async connect(url, body) {
        this.controller = new AbortController();

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
                signal: this.controller.signal,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) {
                    this.onComplete();
                    break;
                }

                // Decode the received chunk and append to buffer
                buffer += decoder.decode(value, { stream: true });

                // Split by double newline which often delimits SSE messages, 
                // or just single newline depending on server implementation.
                // Assuming standard SSE format often uses \n\n between events.
                // If the server sends one line per event with \n, this logic needs adjustment.
                // For robustness, let's treat newlines as separators.
                const lines = buffer.split('\n');

                // The last element is potentially incomplete, keep it in buffer
                buffer = lines.pop() || '';

                for (const line of lines) {
                    const trimmed = line.trim();
                    if (!trimmed) continue;

                    // Helper to parse data
                    if (trimmed.startsWith('data: ')) {
                        const dataStr = trimmed.substring(6);
                        if (dataStr === '[DONE]') {
                            this.onComplete();
                            return;
                        }

                        try {
                            const data = JSON.parse(dataStr);
                            this.onMessage(data);
                        } catch (e) {
                            console.warn('Failed to parse SSE JSON:', e);
                        }
                    }
                }
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('Stream aborted');
            } else {
                console.error('SSE Error:', error);
                this.onError(error);
            }
        }
    }

    abort() {
        if (this.controller) {
            this.controller.abort();
            this.controller = null;
        }
    }
}
