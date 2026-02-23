<template>
  <div class="max-w-6xl mx-auto px-6 py-12">
    <!-- Hero -->
    <div class="text-center mb-16">
      <div class="w-16 h-16 bg-brand-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
        <FileText class="w-8 h-8 text-brand-600" />
      </div>
      <h1 class="text-4xl font-bold text-gray-900 mb-3">PDF Studio</h1>
      <p class="text-lg text-gray-600 max-w-xl mx-auto">
        Edit, merge, split, compress, and convert PDFs — all in your browser.
      </p>
    </div>

    <!-- Quick open -->
    <div class="max-w-lg mx-auto mb-16">
      <FileDropZone
        accept=".pdf"
        label="Open a PDF to start editing"
        hint="Drag & drop or click to browse"
        @files-selected="openEditor"
      />
    </div>

    <!-- Tool cards grid -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      <ToolCard
        v-for="tool in tools"
        :key="tool.route"
        :icon="tool.icon"
        :title="tool.title"
        :description="tool.description"
        :route="tool.route"
        :color="tool.color"
      />
    </div>

    <!-- Recent sessions -->
    <div v-if="recentSessions.length > 0" class="mt-16">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Recent Sessions</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="session in recentSessions"
          :key="session.name"
          class="bg-white border border-gray-200 rounded-xl p-4 hover:border-brand-300 cursor-pointer transition-colors"
          @click="openSession(session)"
        >
          <p class="font-medium text-gray-900 truncate">{{ session.source_file.split('/').pop() }}</p>
          <p class="text-sm text-gray-500 mt-1">{{ session.modified }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FileText } from 'lucide-vue-next'
import FileDropZone from '@/components/shared/FileDropZone.vue'
import ToolCard from '@/components/shared/ToolCard.vue'
import { usePdfApi } from '@/composables/usePdfApi'
import {
  Merge, Split, Minimize2, FileOutput,
  ScanLine, Droplets, Shield, LayoutTemplate
} from 'lucide-vue-next'

const router = useRouter()
const api = usePdfApi()
const recentSessions = ref([])

const tools = [
  {
    route: '/editor',
    icon: FileText,
    title: 'Edit PDF',
    description: 'Annotate, sign, highlight, and modify PDFs',
    color: 'brand',
  },
  {
    route: '/merge',
    icon: Merge,
    title: 'Merge',
    description: 'Combine multiple PDFs into one',
    color: 'blue',
  },
  {
    route: '/split',
    icon: Split,
    title: 'Split',
    description: 'Split PDF into multiple files',
    color: 'green',
  },
  {
    route: '/compress',
    icon: Minimize2,
    title: 'Compress',
    description: 'Reduce PDF file size',
    color: 'amber',
  },
  {
    route: '/convert',
    icon: FileOutput,
    title: 'Convert',
    description: 'PDF to DOCX, DOCX to PDF',
    color: 'red',
  },
  {
    route: '/templates',
    icon: LayoutTemplate,
    title: 'Templates',
    description: 'Design and generate PDFs from templates',
    color: 'purple',
  },
  {
    route: '/batch',
    icon: ScanLine,
    title: 'Batch',
    description: 'Process multiple PDFs at once',
    color: 'indigo',
  },
]

function openEditor(files) {
  if (files.length > 0) {
    // Store file in sessionStorage for the editor to pick up
    const file = files[0]
    window.__pdfStudioFile = file
    router.push('/editor')
  }
}

function openSession(session) {
  router.push(`/editor?session=${session.name}`)
}

onMounted(async () => {
  const result = await api.listSessions()
  if (result?.success) {
    recentSessions.value = result.data.sessions || []
  }
})
</script>
