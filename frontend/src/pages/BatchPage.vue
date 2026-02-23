<template>
  <div class="max-w-3xl mx-auto px-6 py-12">
    <h1 class="text-2xl font-bold text-gray-900 mb-2">Batch Operations</h1>
    <p class="text-gray-600 mb-8">Process multiple PDF files at once.</p>

    <!-- Operation selector -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Operation</label>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="op in operations"
          :key="op.value"
          @click="operation = op.value"
          class="px-4 py-2 rounded-lg text-sm border"
          :class="operation === op.value ? 'bg-brand-50 border-brand-300 text-brand-700' : 'border-gray-300'"
        >
          {{ op.label }}
        </button>
      </div>
    </div>

    <!-- Files -->
    <div v-if="files.length > 0" class="space-y-2 mb-4">
      <div
        v-for="(file, i) in files"
        :key="i"
        class="flex items-center gap-3 bg-white border border-gray-200 rounded-lg px-4 py-2 text-sm"
      >
        <FileText class="w-4 h-4 text-brand-500" />
        <span class="flex-1 truncate">{{ file.name }}</span>
        <button @click="files.splice(i, 1)" class="text-gray-400 hover:text-red-500">
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

    <FileDropZone
      accept=".pdf"
      :multiple="true"
      label="Add PDF files for batch processing"
      @files-selected="addFiles"
      class="mb-6"
    />

    <!-- Options per operation -->
    <div v-if="operation === 'compress'" class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-1">Quality</label>
      <select v-model="options.quality" class="px-3 py-2 border border-gray-300 rounded-lg text-sm">
        <option value="high">Low compression</option>
        <option value="medium">Medium</option>
        <option value="low">Max compression</option>
      </select>
    </div>

    <div v-if="operation === 'watermark'" class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-1">Watermark text</label>
      <input v-model="options.text" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" placeholder="CONFIDENTIAL" />
    </div>

    <div v-if="operation === 'ocr'" class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-1">Language</label>
      <select v-model="options.language" class="px-3 py-2 border border-gray-300 rounded-lg text-sm">
        <option value="eng">English</option>
        <option value="ara">Arabic</option>
        <option value="eng+ara">English + Arabic</option>
      </select>
    </div>

    <!-- Start -->
    <button
      @click="startBatch"
      :disabled="files.length === 0 || processing"
      class="px-6 py-2.5 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 font-medium text-sm"
    >
      {{ processing ? 'Processing...' : `Process ${files.length} files` }}
    </button>

    <p v-if="error" class="mt-3 text-sm text-red-600">{{ error }}</p>

    <!-- Progress -->
    <div v-if="batchName" class="mt-8 bg-white border border-gray-200 rounded-lg p-5">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium">{{ batchStatus }}</span>
        <span class="text-sm text-gray-500">{{ processedFiles }} / {{ totalFiles }}</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div
          class="bg-brand-600 h-2 rounded-full transition-all"
          :style="{ width: `${progress}%` }"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FileText, X } from 'lucide-vue-next'
import FileDropZone from '@/components/shared/FileDropZone.vue'
import { usePdfApi } from '@/composables/usePdfApi'

const api = usePdfApi()
const operation = ref('compress')
const files = ref([])
const options = ref({ quality: 'medium', text: 'CONFIDENTIAL', language: 'eng' })
const processing = ref(false)
const error = ref('')
const batchName = ref('')
const batchStatus = ref('')
const totalFiles = ref(0)
const processedFiles = ref(0)

const operations = [
  { value: 'compress', label: 'Compress' },
  { value: 'watermark', label: 'Watermark' },
  { value: 'ocr', label: 'OCR' },
  { value: 'merge', label: 'Merge All' },
]

const progress = computed(() => totalFiles.value ? (processedFiles.value / totalFiles.value) * 100 : 0)

function addFiles(newFiles) {
  files.value.push(...newFiles)
}

async function startBatch() {
  if (files.value.length === 0) return
  processing.value = true
  error.value = ''

  try {
    // Upload all files
    const urls = []
    for (const file of files.value) {
      const upload = await api.uploadFile(file)
      if (!upload.success) { error.value = `Upload failed: ${upload.error}`; return }
      urls.push(upload.data.file_url)
    }

    // Start batch
    const res = await api.startBatch(operation.value, urls, options.value)
    if (res.success) {
      batchName.value = res.data.batch_name
      batchStatus.value = 'Queued'
      totalFiles.value = files.value.length
      processedFiles.value = 0

      // Poll for status
      pollStatus()
    } else {
      error.value = res.error
    }
  } catch (e) {
    error.value = e.message
  } finally {
    processing.value = false
  }
}

async function pollStatus() {
  const interval = setInterval(async () => {
    const res = await api.getBatchStatus(batchName.value)
    if (res?.success) {
      batchStatus.value = res.data.status
      processedFiles.value = res.data.processed_files

      if (res.data.status === 'Completed' || res.data.status === 'Failed') {
        clearInterval(interval)
        if (res.data.status === 'Failed') {
          error.value = res.data.error || 'Batch failed'
        }
      }
    }
  }, 2000)
}
</script>
