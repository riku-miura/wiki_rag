<script>
    import { chatStore } from '../stores/chat_store';
    
    let query = '';
    
    // Subscribe to store to check loading state
    let isLoading;
    chatStore.subscribe(state => {
        isLoading = state.isLoading;
    });

    function handleSubmit() {
        if (!query.trim() || isLoading) return;
        
        chatStore.sendQuery(query);
        query = '';
    }

    function handleKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
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
        padding: 1rem;
        border-top: 1px solid #eee;
        background: white;
    }

    .input-container {
        display: flex;
        gap: 0.8rem;
        align-items: flex-end;
    }

    textarea {
        flex: 1;
        padding: 0.8rem;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        resize: none;
        height: 60px;
        font-family: inherit;
    }

    textarea:focus {
        outline: none;
        border-color: #007bff;
        box-shadow: 0 0 0 2px rgba(0,123,255,0.1);
    }

    button {
        padding: 0 1.5rem;
        height: 60px;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 0.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
    }

    button:hover:not(:disabled) {
        background-color: #0056b3;
    }

    button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
</style>
