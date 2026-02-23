<template>
  <div class="max-w-3xl mx-auto px-6 py-12">
    <h1 class="text-2xl font-bold text-gray-900 mb-2">Convert</h1>
    <p class="text-gray-600 mb-8">Convert between PDF and other formats.</p>

    <!-- Conversion type -->
    <div class="mb-6">
      <div class="flex gap-3">
        <button
          v-for="mode in modes"
          :key="mode.value"
          @click="conversionMode = mode.value"
          class="px-4 py-2 rounded-lg text-sm border"
          :class="conversionMode === mode.value ? 'bg-brand-50 border-brand-300 text-brand-700' : 'border-gray-300'"
        >
          {{ mode.label }}
        </button>
      </div>
    </div>

    <!-- File upload -->
    <div v-if="!file" class="mb-8">
      <FileDropZone
        :accept="acceptType"
        :label="dropLabel"
        @files-selected="setFile"
      />
    </div>

    <div v-else>
      <div class="flex items-center gap-3 bg-white border border-gray-200 rounded-lg px-4 py-3 mb-6">
        <FileText class="w-5 h-5 text-brand-500" />
        <span class="flex-1 text-sm font-medium">{{ file.name }}</span>
        <button @click="file = null; result = null" class="text-gray-400 hover:text-red-500">
          <X class="w-4 h-4" />
        </button>
      </div>

      <button
        @click="convert"
        :disabled="processing"
        class="px-6 py-2.5 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 font-medium text-sm"
      >
        {{ processing ? 'Converting...' : 'Convert' }}
      </button>

      <p v-if="error" class="mt-3 text-sm text-red-600">{{ error }}</p>

      <div v-if="result" class="mt-8 bg-green-50 border border-green-200 rounded-lg p-4">
        <p class="text-green-800 font-medium">Conversion complete!</p>
        <a :href="result.file_url" download class="text-sm text-brand-600 hover:underline mt-1 inline-block">
          Download {{ result.filename }}
        </a>
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
const conversionMode = ref('pdf-to-docx')
const file = ref(null)
const processing = ref(false)
const error = ref('')
const result = ref(null)

const modes = [
  { value: 'pdf-to-docx', label: 'PDF to DOCX' },
  { value: 'docx-to-pdf', label: 'DOCX to PDF' },
]

const acceptType = computed(() => conversionMode.value === 'pdf-to-docx' ? '.pdf' : '.docx')
const dropLabel = computed(() => conversionMode.value === 'pdf-to-docx' ? 'Select a PDF file' : 'Select a DOCX file')

function setFile(files) {
  if (files.length > 0) file.value = files[0]
}

async function convert() {
  if (!file.value) return
  processing.value = true
  error.value = ''
  result.value = null

  try {
    const upload = await api.uploadFile(file.value)
    if (!upload.success) { error.value = upload.error; return }

    let res
    if (conversionMode.value === 'pdf-to-docx') {
      res = await api.pdfToDocx(upload.data.file_url)
    } else {
      res = await api.docxToPdf(upload.data.file_url)
    }

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
</script>
