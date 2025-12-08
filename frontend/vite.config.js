import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// This configuration ensures Vite knows where the entry points are.
export default defineConfig({
  // Base directory for serving files (usually the project root)
  root: './', 
  plugins: [vue()],
  server: {
    // The port the Vue dev server runs on (needed for debugging cross-origin issues)
    port: 5173 
  },
  // Build configuration to ensure correct output directory and entry HTML
  build: {
    outDir: 'dist', // Standard output directory
    rollupOptions: {
      input: {
        // Explicitly defining the HTML entry point
        main: './index.html', 
      }
    }
  }
})