<script>
    export let messages = [];
    import { afterUpdate } from 'svelte';

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
                    {new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </div>
            </div>
        </div>
    {/each}
</div>

<style>
    .message-list {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
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
        padding: 0.8rem 1.2rem;
        border-radius: 1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }

    .user .bubble {
        background-color: #007bff;
        color: white;
        border-bottom-right-radius: 0.2rem;
    }

    .assistant .bubble {
        background-color: #f1f3f5;
        color: #333;
        border-bottom-left-radius: 0.2rem;
    }
    
    .system .bubble {
        background-color: transparent;
        box-shadow: none;
        color: #666;
        text-align: center;
    }

    .time {
        font-size: 0.7rem;
        margin-top: 0.4rem;
        opacity: 0.7;
        text-align: right;
    }
</style>
