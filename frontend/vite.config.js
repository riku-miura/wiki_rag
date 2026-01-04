import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [svelte()],
    base: '/projects/wiki_rag/', // Base path for subdirectory deployment
    define: {
        'import.meta.env.VITE_API_URL': JSON.stringify('https://qsmdcp3sr1.execute-api.ap-northeast-1.amazonaws.com/prod')
    }
})
