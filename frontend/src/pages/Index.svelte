<script>
    import { chatStore } from "../stores/chat_store";
    import WikipediaInput from "../components/WikipediaInput.svelte";
    import StatusIndicator from "../components/StatusIndicator.svelte";

    let status = "idle";
    let errorMessage = "";

    chatStore.subscribe((state) => {
        status = state.ragStatus;
        errorMessage = state.error || "";
        // Note: navigation to Chat page happens in App.svelte when sessionId is set
    });

    function handleUrlSubmit(event) {
        const { url } = event.detail;
        chatStore.buildRag(url).catch((err) => {
            console.error("Build failed", err);
        });
    }
</script>

<div class="index-page">
    <header>
        <h1>Wikipedia RAG</h1>
        <p>Wikipediaの記事についてチャットで質問できます！</p>
    </header>

    <main>
        <WikipediaInput
            on:submit={handleUrlSubmit}
            isLoading={status === "building"}
        />

        <StatusIndicator {status} message={errorMessage} />
    </main>
</div>

<style>
    .index-page {
        min-height: 100vh;
        padding: 2rem;
        background-color: #f8f9fa;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    header {
        text-align: center;
        margin-bottom: 3rem;
    }

    h1 {
        font-size: 3rem;
        margin: 0;
        color: #2c3e50;
    }

    p {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0.5rem;
    }

    main {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
</style>
