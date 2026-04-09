import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../../static/flujos/dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        // Nombres fijos sin hash — el template Django los referencia directamente
        entryFileNames: 'assets/index.js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]',
      },
    },
  },
  server: {
    // En dev local, proxy para no tener problemas de CORS con la API Django
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});
