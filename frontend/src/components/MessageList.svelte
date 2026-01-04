<script>
    export let messages = [];
    import { afterUpdate } from "svelte";

    let container;

    afterUpdate(() => {
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    });
</script>

<div class="message-list" bind:this={container}>
    {#each messages as msg}
        <div class="message {msg.role}">
            <div class="bubble">
                <div class="content">{msg.content}</div>
                <div class="time">
                    {new Date(msg.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                    })}
                </div>
            </div>
        </div>
    {/each}
</div>

<style>
    .message-list {
        flex: 1;
        overflow-y: auto;
        padding: var(--space-4);
        display: flex;
        flex-direction: column;
        gap: var(--space-4);
    }

    .message {
        display: flex;
        width: 100%;
    }

    .message.user {
        justify-content: flex-end;
    }

    .message.assistant {
        justify-content: flex-start;
    }

    .message.system {
        justify-content: center;
        opacity: 0.7;
        font-size: 0.9rem;
    }

    .bubble {
        max-width: 80%;
        padding: var(--space-2) 1.2rem;
        border-radius: var(--radius-2xl);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        color: var(--color-text);
    }

    .user .bubble {
        background-color: var(--color-primary);
        color: var(--color-background);
        border-bottom-right-radius: var(--radius-sm);
    }

    .assistant .bubble {
        background-color: var(--color-background);
        border: 1px solid var(--color-border);
        color: var(--color-text-secondary);
        border-bottom-left-radius: var(--radius-sm);
    }

    .system .bubble {
        background-color: transparent;
        box-shadow: none;
        color: var(--color-text-muted);
        text-align: center;
    }

    .time {
        font-size: 0.7rem;
        margin-top: 0.4rem;
        opacity: 0.7;
        text-align: right;
    }
</style>
