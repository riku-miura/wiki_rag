<script>
    import { createEventDispatcher } from 'svelte';
    
    export let isLoading = false;
    let url = '';
    
    const dispatch = createEventDispatcher();

    function handleSubmit() {
        if (!url || isLoading) return;
        dispatch('submit', { url });
    }
</script>

<div class="wiki-input">
    <h2>Build Knowledge Base</h2>
    <p>Enter a Wikipedia URL to start chatting with it.</p>
    
    <div class="input-group">
        <input 
            type="url" 
            bind:value={url} 
            placeholder="https://en.wikipedia.org/wiki/..." 
            disabled={isLoading}
        />
        <button on:click={handleSubmit} disabled={!url || isLoading}>
            {#if isLoading}
                Building...
            {:else}
                Start
            {/if}
        </button>
    </div>
</div>

<style>
    .wiki-input {
        text-align: center;
        max-width: 600px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    h2 {
        margin-top: 0;
        color: #333;
    }
    
    p {
        color: #666;
        margin-bottom: 1.5rem;
    }

    .input-group {
        display: flex;
        gap: 0.5rem;
    }

    input {
        flex: 1;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        font-size: 1rem;
    }

    button {
        padding: 0 2rem;
        background-color: #28a745;
        color: white;
        border: none;
        border-radius: 0.5rem;
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
    }

    button:hover:not(:disabled) {
        background-color: #218838;
    }

    button:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }
</style>
