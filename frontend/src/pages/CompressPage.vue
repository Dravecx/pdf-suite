<template>
  <div class="max-w-3xl mx-auto px-6 py-12">
    <h1 class="text-2xl font-bold text-gray-900 mb-2">Compress PDF</h1>
    <p class="text-gray-600 mb-8">Reduce PDF file size while maintaining quality.</p>

    <div v-if="!file" class="mb-8">
      <FileDropZone accept=".pdf" label="Select a PDF to compress" @files-selected="setFile" />
    </div>

    <div v-else>
      <div class="flex items-center gap-3 bg-white border border-gray-200 rounded-lg px-4 py-3 mb-6">
        <FileText class="w-5 h-5 text-brand-500" />
        <span class="flex-1 text-sm font-medium">{{ file.name }}</span>
        <span class="text-xs text-gray-500">{{ humanSize(file.size) }}</span>
        <button @click="file = null; result = null" class="text-gray-400 hover:text-red-500">
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Quality selector -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">Compression level</label>
        <div class="flex gap-3">
          <button
            v-for="q in qualities"
            :key="q.value"
            @click="quality = q.value"
            class="flex-1 px-4 py-3 rounded-lg border text-center"
            :class="quality === q.value ? 'bg-brand-50 border-brand-300' : 'border-gray-200 hover:border-gray-300'"
          >
            <p class="font-medium text-sm" :class="quality === q.value ? 'text-brand-700' : 'text-gray-800'">{{ q.label }}</p>
            <p class="text-xs text-gray-500 mt-0.5">{{ q.desc }}</p>
          </button>
        </div>
      </div>

      <button
        @click="compress"
        :disabled="processing"
        class="px-6 py-2.5 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 font-medium text-sm"
      >
        {{ processing ? 'Compressing...' : 'Compress PDF' }}
      </button>

      <p v-if="error" class="mt-3 text-sm text-red-600">{{ error }}</p>

      <!-- Result -->
      <div v-if="result" class="mt-8 bg-green-50 border border-green-200 rounded-lg p-5">
        <div class="flex items-center justify-between mb-3">
          <p class="text-green-800 font-medium">Compression complete!</p>
          <span class="text-sm font-semibold text-green-700">-{{ result.reduction_percent }}%</span>
        </div>
        <div class="flex items-center gap-6 text-sm text-gray-700">
          <div>
            <span class="text-gray-500">Original:</span>
            <span class="ml-1 font-medium">{{ result.original_size_human }}</span>
          </div>
          <ArrowRight class="w-4 h-4 text-gray-400" />
          <div>
            <span class="text-gray-500">Compressed:</span>
            <span class="ml-1 font-medium">{{ result.compressed_size_human }}</span>
          </div>
        </div>
        <a :href="result.file_url" download class="text-sm text-brand-600 hover:underline mt-3 inline-block">
          Download compressed PDF
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FileText, X, ArrowRight } from 'lucide-vue-next'
import FileDropZone from '@/components/shared/FileDropZone.vue'
import { usePdfApi } from '@/composables/usePdfApi'

const api = usePdfApi()
const file = ref(null)
const quality = ref('medium')
const processing = ref(false)
const error = ref('')
const result = ref(null)

const qualities = [
  { value: 'high', label: 'Low', desc: 'Minimal compression' },
  { value: 'medium', label: 'Medium', desc: 'Balanced' },
  { value: 'low', label: 'High', desc: 'Max compression' },
]

function setFile(files) {
  if (files.length > 0) file.value = files[0]
}

async function compress() {
  if (!file.value) return
  processing.value = true
  error.value = ''
  result.value = null

  try {
    const upload = await api.uploadFile(file.value)
    if (!upload.success) { error.value = upload.error; return }

    const res = await api.compressPdf(upload.data.file_url, quality.value)
    if (res.success) {
      result.value = res.data
    } else {
      error.value = res.error
    }
  } catch (e) {
    error.value = e.message
  } finally {
    processing.value = false
  }
}

function humanSize(bytes) {
  for (const unit of ['B', 'KB', 'MB', 'GB']) {
    if (bytes < 1024) return `${bytes.toFixed(1)} ${unit}`
    bytes /= 1024
  }
  return `${bytes.toFixed(1)} TB`
}
</script>
