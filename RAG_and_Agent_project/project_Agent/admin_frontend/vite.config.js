import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 后台管理前端构建配置
// dev 模式：/api 代理到 FastAPI 后台（:8001）
// build 模式：产物输出到 dist/，由 FastAPI 静态托管
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
