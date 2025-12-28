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
    :global(body) {
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
    }
    
    main {
        width: 100%;
        height: 100vh;
    }
</style>
