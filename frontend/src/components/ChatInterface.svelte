<script>
    import { chatStore } from "../stores/chat_store";

    let query = "";

    // Subscribe to store to check loading state
    let isLoading;
    chatStore.subscribe((state) => {
        isLoading = state.isLoading;
    });

    function handleSubmit() {
        if (!query.trim() || isLoading) return;

        chatStore.sendQuery(query);
        query = "";
    }

    function handleKeydown(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    }
</script>

<div class="chat-interface">
    <div class="input-container">
        <textarea
            bind:value={query}
            on:keydown={handleKeydown}
            placeholder="Ask a question about the article..."
            disabled={isLoading}
        ></textarea>
        <button on:click={handleSubmit} disabled={!query.trim() || isLoading}>
            {#if isLoading}
                <span>...</span>
            {:else}
                Send
            {/if}
        </button>
    </div>
</div>

<style>
    .chat-interface {
        padding: var(--space-4);
        border-top: 1px solid var(--color-border);
        background: var(--color-background);
    }

    .input-container {
        display: flex;
        gap: var(--space-2);
        align-items: flex-end;
    }

    textarea {
        flex: 1;
        padding: var(--space-2);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        resize: none;
        height: 60px;
        font-family: inherit;
        background: var(--color-background);
        color: var(--color-text);
    }

    textarea:focus {
        outline: none;
        border-color: var(--color-focus);
        box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.1);
    }

    button {
        padding: 0 var(--space-6);
        height: 60px;
        background-color: var(--color-primary);
        color: var(--color-background);
        border: none;
        border-radius: var(--radius-lg);
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
    }

    button:hover:not(:disabled) {
        background-color: var(--color-primary-hover);
    }

    button:disabled {
        background-color: var(--color-border);
        color: var(--color-text-muted);
        cursor: not-allowed;
    }
</style>
