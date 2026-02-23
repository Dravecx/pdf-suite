<template>
  <div class="max-w-3xl mx-auto px-6 py-12">
    <h1 class="text-2xl font-bold text-gray-900 mb-2">Split PDF</h1>
    <p class="text-gray-600 mb-8">Split a PDF into multiple files by page ranges.</p>

    <!-- File upload -->
    <div v-if="!file" class="mb-8">
      <FileDropZone accept=".pdf" label="Select a PDF to split" @files-selected="setFile" />
    </div>

    <div v-else>
      <!-- File info -->
      <div class="flex items-center gap-3 bg-white border border-gray-200 rounded-lg px-4 py-3 mb-6">
        <FileText class="w-5 h-5 text-brand-500" />
        <span class="flex-1 text-sm font-medium">{{ file.name }}</span>
        <button @click="file = null" class="text-gray-400 hover:text-red-500">
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Split mode -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">Split mode</label>
        <div class="flex gap-3">
          <button
            @click="splitMode = 'ranges'"
            class="px-4 py-2 rounded-lg text-sm border"
            :class="splitMode === 'ranges' ? 'bg-brand-50 border-brand-300 text-brand-700' : 'border-gray-300'"
          >
            By page ranges
          </button>
          <button
            @click="splitMode = 'every'"
            class="px-4 py-2 rounded-lg text-sm border"
            :class="splitMode === 'every' ? 'bg-brand-50 border-brand-300 text-brand-700' : 'border-gray-300'"
          >
            Every N pages
          </button>
          <button
            @click="splitMode = 'extract'"
            class="px-4 py-2 rounded-lg text-sm border"
            :class="splitMode === 'extract' ? 'bg-brand-50 border-brand-300 text-brand-700' : 'border-gray-300'"
          >
            Extract pages
          </button>
        </div>
      </div>

      <!-- Range inputs -->
      <div v-if="splitMode === 'ranges'" class="mb-6">
        <div v-for="(range, i) in ranges" :key="i" class="flex items-center gap-2 mb-2">
          <PageRangeInput v-model="ranges[i]" class="flex-1" />
          <button v-if="ranges.length > 1" @click="ranges.splice(i, 1)" class="p-2 text-red-400 hover:text-red-600">
            <X class="w-4 h-4" />
          </button>
        </div>
        <button @click="ranges.push('')" class="text-sm text-brand-600 hover:underline">
          + Add range
        </button>
      </div>

      <div v-if="splitMode === 'every'" class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-1">Pages per file</label>
        <input v-model.number="everyN" type="number" min="1" class="w-32 px-3 py-2 border border-gray-300 rounded-lg text-sm" />
      </div>

      <div v-if="splitMode === 'extract'" class="mb-6">
        <PageRangeInput v-model="extractPages" label="Pages to extract" />
      </div>

      <!-- Action -->
      <button
        @click="split"
        :disabled="processing"
        class="px-6 py-2.5 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 font-medium text-sm"
      >
        {{ processing ? 'Processing...' : 'Split PDF' }}
      </button>

      <p v-if="error" class="mt-3 text-sm text-red-600">{{ error }}</p>

      <!-- Results -->
      <div v-if="results.length > 0" class="mt-8 space-y-2">
        <p class="font-medium text-green-800 mb-2">Split complete! {{ results.length }} files created.</p>
        <a
          v-for="(r, i) in results"
          :key="i"
          :href="r.file_url"
          download
          class="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-4 py-2 hover:border-brand-300 text-sm"
        >
          <Download class="w-4 h-4 text-brand-500" />
          <span>{{ r.filename }}</span>
          <span class="text-gray-400 ml-auto">{{ r.pages }} pages</span>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FileText, X, Download } from 'lucide-vue-next'
import FileDropZone from '@/components/shared/FileDropZone.vue'
import PageRangeInput from '@/components/shared/PageRangeInput.vue'
import { usePdfApi } from '@/composables/usePdfApi'

const api = usePdfApi()
const file = ref(null)
const splitMode = ref('ranges')
const ranges = ref([''])
const everyN = ref(1)
const extractPages = ref('')
const processing = ref(false)
const error = ref('')
const results = ref([])

function setFile(files) {
  if (files.length > 0) file.value = files[0]
}

async function split() {
  if (!file.value) return

  processing.value = true
  error.value = ''
  results.value = []

  try {
    // Upload file
    const upload = await api.uploadFile(file.value)
    if (!upload.success) {
      error.value = upload.error
      return
    }

    let result
    if (splitMode.value === 'ranges') {
      result = await api.splitPdf(upload.data.file_url, ranges.value.filter(r => r.trim()))
    } else if (splitMode.value === 'every') {
      result = await api.splitEveryN(upload.data.file_url, everyN.value)
    } else {
      result = await api.extractPages(upload.data.file_url, extractPages.value)
    }

    if (result.success) {
      results.value = result.data.files || [result.data]
    } else {
      error.value = result.error
    }
  } catch (e) {
    error.value = e.message
  } finally {
    processing.value = false
  }
}
</script>
