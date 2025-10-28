import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('react-')
        }
      }
    }),
    react({
      jsxRuntime: 'automatic'
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@vue': resolve(__dirname, 'src/vue'),
      '@react': resolve(__dirname, 'src/react'),
      '@shared': resolve(__dirname, 'src/shared')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia', 'element-plus'],
          'react-vendor': ['react', 'react-dom', 'react-router-dom', '@reduxjs/toolkit', 'react-redux', 'antd'],
          'shared-vendor': ['axios', 'dayjs', 'lodash', 'quill']
        }
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  }
})