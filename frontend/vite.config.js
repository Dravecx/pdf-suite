import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ command }) => ({
  base: command === 'serve' ? '/' : '/assets/pdf_suite/dist/',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3002,
    open: true,
    proxy: {
      '^/(api|app|login|assets|files|private)': {
        target: 'https://codebase.u.frappe.cloud',
        changeOrigin: true,
        secure: true,
        ws: true,
        cookieDomainRewrite: {
          'codebase.u.frappe.cloud': 'localhost',
          '.frappe.cloud': 'localhost',
        },
        cookiePathRewrite: { '*': '/' },
        onProxyRes(proxyRes) {
          const cookies = proxyRes.headers['set-cookie']
          if (cookies) {
            proxyRes.headers['set-cookie'] = cookies.map((c) =>
              c
                .replace(/Domain=[^;]+;?/gi, '')
                .replace(/Secure;?/gi, '')
                .replace(/SameSite=None;?/gi, 'SameSite=Lax;')
            )
          }
        },
      },
    },
  },
  build: {
    outDir: path.resolve(__dirname, '..', 'pdf_suite', 'public', 'dist'),
    emptyOutDir: true,
    target: 'es2015',
    sourcemap: true,
    rollupOptions: {
      output: {
        entryFileNames: '[name]-[hash].js',
        chunkFileNames: '[name]-[hash].js',
        assetFileNames: '[name]-[hash].[ext]',
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('pdfjs-dist')) return 'pdf-js'
            if (id.includes('/fabric/') || id.includes('fabric/src')) return 'fabric'
            if (id.includes('pdf-lib')) return 'pdf-lib'
            if (id.includes('vue') || id.includes('pinia')) return 'vue-vendor'
            if (id.includes('lucide-vue-next')) return 'icons'
          }
        },
      },
    },
  },
}))
