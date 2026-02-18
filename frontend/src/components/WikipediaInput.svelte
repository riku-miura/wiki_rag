<script>
    import { createEventDispatcher } from "svelte";

    export let isLoading = false;
    let url = "";
    let error = "";

    const dispatch = createEventDispatcher();

    function handleSubmit() {
        if (!url || isLoading) return;

        if (!url.startsWith("https://ja.wikipedia.org/wiki/")) {
            error =
                "日本語のWikipedia URL (https://ja.wikipedia.org/wiki/...) を入力してください。";
            return;
        }

        error = "";
        dispatch("submit", { url });
    }
</script>

<div class="wiki-input">
    <h2>ナレッジベース構築</h2>
    <p>WikipediaのURLを入力して、チャットを開始しましょう。</p>

    <div class="input-container">
        <div class="input-group">
            <input
                type="url"
                bind:value={url}
                placeholder="https://ja.wikipedia.org/wiki/..."
                disabled={isLoading}
                on:input={() => (error = "")}
            />
            <button on:click={handleSubmit} disabled={!url || isLoading}>
                {#if isLoading}
                    処理中...
                {:else}
                    開始
                {/if}
            </button>
        </div>
        {#if error}
            <div class="error-message">{error}</div>
        {/if}
    </div>
</div>

<style>
    .wiki-input {
        text-align: center;
        max-width: 600px;
        margin: 2rem auto;
        padding: var(--space-6);
        background: var(--color-background);
        border-radius: var(--radius-lg);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--color-border);
    }

    h2 {
        margin-top: 0;
        color: var(--color-text);
    }

    p {
        color: var(--color-text-muted);
        margin-bottom: var(--space-6);
    }

    .input-group {
        display: flex;
        gap: var(--space-2);
    }

    input {
        flex: 1;
        padding: var(--space-4);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        font-size: 1rem;
        background: var(--color-background);
        color: var(--color-text);
    }

    button {
        padding: 0 var(--space-6);
        background-color: var(--color-primary);
        color: var(--color-background);
        border: none;
        border-radius: var(--radius-lg);
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
    }

    button:hover:not(:disabled) {
        background-color: var(--color-primary-hover);
    }

    button:disabled {
        background-color: var(--color-border);
        color: var(--color-text-muted);
        cursor: not-allowed;
    }

    .error-message {
        color: #dc3545;
        font-size: 0.9rem;
        margin-top: var(--space-2);
        text-align: left;
    }
</style>
