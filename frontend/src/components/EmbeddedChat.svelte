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
                <h3>Wiki RAG チャット</h3>
                <button on:click={toggleChat} class="close-btn">
                    <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </header>
            <div class="messages-area">
                {#if !sessionId && !initialUrl}
                    <div class="start-prompt">
                        <p>開始するにはWikipediaのURLを設定してください。</p>
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

    <button
        class="chat-launcher"
        on:click={toggleChat}
        class:open={isOpen}
        aria-label="Toggle Chat"
    >
        {#if isOpen}
            <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
            >
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        {:else}
            <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
            >
                <path
                    d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                ></path>
            </svg>
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
        background-color: var(--color-primary);
        color: var(--color-background);
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s;
    }

    .chat-launcher:hover {
        background-color: var(--color-primary-hover);
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
        background: var(--color-background);
        border-radius: var(--radius-lg);
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid var(--color-border);
    }

    header {
        padding: var(--space-4);
        background: var(--color-primary);
        color: var(--color-background);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    header h3 {
        margin: 0;
        font-size: 1rem;
        color: var(--color-background);
    }

    .close-btn {
        background: none;
        border: none;
        color: var(--color-background);
        cursor: pointer;
        padding: 0;
        display: flex;
        align-items: center;
    }

    .messages-area {
        flex: 1;
        overflow-y: auto;
        padding: 0;
        display: flex;
        flex-direction: column;
    }

    footer {
        border-top: 1px solid var(--color-border);
    }

    .start-prompt {
        padding: var(--space-6);
        text-align: center;
        color: var(--color-text-muted);
    }
</style>
