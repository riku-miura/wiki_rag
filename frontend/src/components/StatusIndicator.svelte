<script>
    export let status = "idle"; // idle, building, ready, error
    export let message = "";
</script>

{#if status !== "idle"}
    <div class="status-indicator {status}">
        <div class="icon">
            {#if status === "building"}
                Processing...
            {:else if status === "ready"}
                Ready
            {:else if status === "error"}
                Error
            {/if}
        </div>
        <div class="text">
            <strong>{status.toUpperCase()}</strong>
            {#if message}
                <span>: {message}</span>
            {/if}
        </div>
    </div>
{/if}

<style>
    .status-indicator {
        display: flex;
        align-items: center;
        gap: var(--space-4);
        padding: var(--space-4);
        border-radius: var(--radius-lg);
        margin: var(--space-4) 0;
        border: 1px solid var(--color-border);
    }

    .building {
        background-color: var(--color-background-secondary);
        color: var(--color-primary);
    }

    .ready {
        background-color: var(--color-background);
        color: var(--color-text);
        border-color: var(--color-primary);
    }

    .error {
        background-color: var(--color-background-secondary);
        color: var(--color-text-muted);
        border-color: var(--color-text-muted);
    }

    .icon {
        font-size: 1.2rem;
        font-weight: bold;
    }

    .building .icon {
        animation: pulse 1.5s infinite;
        display: inline-block;
    }

    @keyframes pulse {
        0% {
            opacity: 0.5;
        }
        50% {
            opacity: 1;
        }
        100% {
            opacity: 0.5;
        }
    }
</style>
