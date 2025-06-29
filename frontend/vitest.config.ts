/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'clover', 'json'],
      reportsDirectory: './coverage',
      enabled: true,
      reportOnFailure: true,
      exclude: [
        'node_modules/',
        'src/test-setup.ts',
        '**/*.config.ts',
        '**/*.config.js',
        'dist/',
        'coverage/',
        '**/*.d.ts'
      ],
      skipFull: false,
      all: true
    }
  }
})