<script>
    import { chatStore } from '../stores/chat_store';
    import MessageList from '../components/MessageList.svelte';
    import ChatInterface from '../components/ChatInterface.svelte';
    import { onMount } from 'svelte';

    let messages = [];
    let sessionId;

    chatStore.subscribe(state => {
        messages = state.messages;
        sessionId = state.sessionId;
    });
    
    onMount(() => {
        if (sessionId) {
            // Fetch history on load if needed, but store might already have it or be fresh
            // apiClient.getHistory(sessionId).then(...)
        }
    });

    function handleBack() {
        chatStore.reset();
    }
</script>

<div class="chat-page">
    <header>
        <button on:click={handleBack} class="back-btn">← Back</button>
        <h1>Chat Session</h1>
    </header>
    
    <main>
        <MessageList {messages} />
    </main>

    <footer>
        <ChatInterface />
    </footer>
</div>

<style>
    .chat-page {
        display: flex;
        flex-direction: column;
        height: 100vh;
        max-width: 800px;
        margin: 0 auto;
        background: #f9f9f9;
        box-shadow: 0 0 20px rgba(0,0,0,0.05);
    }

    header {
        padding: 1rem;
        background: white;
        border-bottom: 1px solid #eee;
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    header h1 {
        margin: 0;
        font-size: 1.2rem;
    }

    .back-btn {
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        font-size: 1rem;
    }
    
    .back-btn:hover {
        color: #333;
    }

    main {
        flex: 1;
        overflow: hidden; /* Scroll handled by MessageList */
        display: flex;
        flex-direction: column;
    }
</style>
