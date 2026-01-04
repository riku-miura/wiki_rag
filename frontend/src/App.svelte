<script>
    import { chatStore } from './stores/chat_store';
    import Index from './pages/Index.svelte';
    import Chat from './pages/Chat.svelte';

    let sessionId;
    
    chatStore.subscribe(state => {
        sessionId = state.sessionId;
    });
</script>

<main>
    {#if sessionId}
        <Chat />
    {:else}
        <Index />
    {/if}
</main>

<style>
    :global(:root) {
        /* Colors - Personal Page Palette */
        --color-primary: #0066cc;
        --color-primary-hover: #0056b3;
        --color-text: #000000;
        --color-text-secondary: #333333;
        --color-text-muted: #666666;
        --color-background: #ffffff;
        --color-background-secondary: #f8f9fa;
        --color-border: #e0e0e0;
        --color-focus: #0066cc;

        /* Spacing */
        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-4: 1rem;
        --space-6: 1.5rem;

        /* Radius */
        --radius-md: 4px;
        --radius-lg: 8px;
    }

    :global(body) {
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: var(--color-background-secondary);
        color: var(--color-text);
        line-height: 1.6;
    }
    
    main {
        width: 100%;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }
</style>
