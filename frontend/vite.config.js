import { defineConfig } from 'vite'

export default defineConfig({
  root: 'frontend',
  build: {
    outDir: '../backend/app/static',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: 'frontend/src/pages/index.html',
        jam: 'frontend/src/pages/jam.html',
        songs: 'frontend/src/pages/songs.html',
        jams: 'frontend/src/pages/jams.html',
        admin: 'frontend/src/pages/admin.html'
      }
    }
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': 'http://localhost:8000'
    }
  }
})
