<template>
  <div class="max-w-3xl mx-auto px-6 py-12">
    <h1 class="text-2xl font-bold text-gray-900 mb-2">Merge PDFs</h1>
    <p class="text-gray-600 mb-8">Combine multiple PDF files into a single document.</p>

    <!-- File list -->
    <div v-if="files.length > 0" class="space-y-2 mb-6">
      <div
        v-for="(file, index) in files"
        :key="index"
        class="flex items-center gap-3 bg-white border border-gray-200 rounded-lg px-4 py-3"
      >
        <GripVertical class="w-4 h-4 text-gray-400 cursor-grab" />
        <FileText class="w-5 h-5 text-brand-500" />
        <span class="flex-1 text-sm text-gray-800 truncate">{{ file.name }}</span>
        <span class="text-xs text-gray-500">{{ humanSize(file.size) }}</span>
        <button @click="removeFile(index)" class="p-1 hover:bg-red-50 rounded text-red-400 hover:text-red-600">
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Drop zone -->
    <FileDropZone
      accept=".pdf"
      :multiple="true"
      label="Add PDF files to merge"
      hint="You can add multiple files. Drag to reorder."
      @files-selected="addFiles"
      class="mb-8"
    />

    <!-- Output name -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-1">Output filename</label>
      <input
        v-model="outputName"
        type="text"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500"
        placeholder="merged.pdf"
      />
    </div>

    <!-- Actions -->
    <div class="flex items-center gap-3">
      <button
        @click="merge"
        :disabled="files.length < 2 || processing"
        class="px-6 py-2.5 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 font-medium text-sm"
      >
        {{ processing ? 'Merging...' : 'Merge PDFs' }}
      </button>

      <span v-if="error" class="text-sm text-red-600">{{ error }}</span>
    </div>

    <!-- Result -->
    <div v-if="result" class="mt-8 bg-green-50 border border-green-200 rounded-lg p-4">
      <p class="text-green-800 font-medium">Merge complete!</p>
      <a
        :href="result.file_url"
        download
        class="text-sm text-brand-600 hover:underline mt-1 inline-block"
      >
        Download {{ result.filename }}
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FileText, GripVertical, X } from 'lucide-vue-next'
import FileDropZone from '@/components/shared/FileDropZone.vue'
import { usePdfApi } from '@/composables/usePdfApi'

const api = usePdfApi()
const files = ref([])
const outputName = ref('merged.pdf')
const processing = ref(false)
const error = ref('')
const result = ref(null)

function addFiles(newFiles) {
  files.value.push(...newFiles)
}

function removeFile(index) {
  files.value.splice(index, 1)
}

async function merge() {
  if (files.value.length < 2) return

  processing.value = true
  error.value = ''
  result.value = null

  try {
    // Upload all files first
    const uploadResults = []
    for (const file of files.value) {
      const res = await api.uploadFile(file)
      if (!res.success) {
        error.value = `Failed to upload ${file.name}: ${res.error}`
        return
      }
      uploadResults.push(res.data.file_url)
    }

    // Call merge API
    const mergeResult = await api.mergePdfs(uploadResults, outputName.value)
    if (mergeResult.success) {
      result.value = mergeResult.data
    } else {
      error.value = mergeResult.error || 'Merge failed'
    }
  } catch (e) {
    error.value = e.message || 'Network error'
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
