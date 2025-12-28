<script>
    export let status = 'idle'; // idle, building, ready, error
    export let message = '';
</script>

{#if status !== 'idle'}
    <div class="status-indicator {status}">
        <div class="icon">
            {#if status === 'building'}
                🔄
            {:else if status === 'ready'}
                ✅
            {:else if status === 'error'}
                ❌
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
        gap: 1rem;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    .building {
        background-color: #e3f2fd;
        color: #0d47a1;
    }

    .ready {
        background-color: #e8f5e9;
        color: #1b5e20;
    }

    .error {
        background-color: #ffebee;
        color: #b71c1c;
    }

    .icon {
        font-size: 1.5rem;
    }
    
    .building .icon {
        animation: spin 2s linear infinite;
        display: inline-block;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
