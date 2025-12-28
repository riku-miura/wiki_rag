<script>
    import { chatStore } from "../stores/chat_store";
    import ChatInterface from "./ChatInterface.svelte";
    import MessageList from "./MessageList.svelte";
    import { onMount } from "svelte";

    export let initialUrl = ""; // allow pre-setting URL

    let sessionId;
    let messages = [];
    let isOpen = false;

    chatStore.subscribe((state) => {
        sessionId = state.sessionId;
        messages = state.messages;
    });

    onMount(() => {
        if (initialUrl) {
            chatStore.buildRag(initialUrl).catch(console.error);
        }
    });

    function toggleChat() {
        isOpen = !isOpen;
    }
</script>

<div class="embedded-chat-container">
    {#if isOpen}
        <div class="chat-window">
            <header>
                <h3>Wiki RAG Chat</h3>
                <button on:click={toggleChat} class="close-btn">×</button>
            </header>
            <div class="messages-area">
                {#if !sessionId && !initialUrl}
                    <div class="start-prompt">
                        <p>Please configure a Wikipedia URL to start.</p>
                        <!-- Simplification: For embedded, usually the parent page sets context -->
                    </div>
                {:else}
                    <MessageList {messages} />
                {/if}
            </div>
            <footer>
                <ChatInterface />
            </footer>
        </div>
    {/if}

    <button class="chat-launcher" on:click={toggleChat} class:open={isOpen}>
        {#if isOpen}
            💬
        {:else}
            🤖
        {/if}
    </button>
</div>

<style>
    .embedded-chat-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        font-family: -apple-system, system-ui, sans-serif;
    }

    .chat-launcher {
        width: 60px;
        height: 60px;
        border-radius: 30px;
        background-color: #007bff;
        color: white;
        border: none;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .chat-launcher:hover {
        transform: scale(1.05);
    }

    .chat-launcher.open {
        transform: rotate(90deg);
    }

    .chat-window {
        position: absolute;
        bottom: 80px;
        right: 0;
        width: 350px;
        height: 500px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid #eee;
    }

    header {
        padding: 1rem;
        background: #007bff;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    header h3 {
        margin: 0;
        font-size: 1rem;
    }

    .close-btn {
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        line-height: 1;
    }

    .messages-area {
        flex: 1;
        overflow-y: auto;
        padding: 0;
        display: flex;
        flex-direction: column;
    }

    footer {
        border-top: 1px solid #eee;
    }

    .start-prompt {
        padding: 2rem;
        text-align: center;
        color: #666;
    }
</style>
