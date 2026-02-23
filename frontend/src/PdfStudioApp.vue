<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Top nav bar (only on non-editor pages) -->
    <header v-if="!isEditorRoute" class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <router-link to="/" class="flex items-center gap-2 text-xl font-semibold text-gray-900">
        <FileText class="w-6 h-6 text-brand-600" />
        <span>PDF Studio</span>
      </router-link>
      <nav class="flex items-center gap-4">
        <router-link
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="text-sm text-gray-600 hover:text-brand-600 transition-colors"
          active-class="text-brand-600 font-medium"
        >
          {{ link.label }}
        </router-link>
      </nav>
    </header>

    <!-- Main content -->
    <main class="flex-1">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { FileText } from 'lucide-vue-next'

const route = useRoute()

const isEditorRoute = computed(() => route.name === 'editor')

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/merge', label: 'Merge' },
  { to: '/split', label: 'Split' },
  { to: '/compress', label: 'Compress' },
  { to: '/convert', label: 'Convert' },
  { to: '/templates', label: 'Templates' },
  { to: '/batch', label: 'Batch' },
]
</script>
