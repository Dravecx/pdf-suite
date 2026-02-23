<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-xl mx-auto px-6 py-10">

      <!-- Header -->
      <div class="flex items-center gap-3 mb-8">
        <button
          class="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 transition-colors"
          @click="$router.push('/templates')"
        >
          <ArrowLeft class="w-4 h-4" />
          Templates
        </button>
        <div class="w-px h-4 bg-gray-200" />
        <span class="text-sm text-gray-500">Generate PDF</span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-16">
        <div class="w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
      </div>

      <!-- Not found -->
      <div v-else-if="!template" class="text-center py-16">
        <p class="text-red-600 mb-3">Template not found.</p>
        <button @click="$router.push('/templates')" class="text-sm text-orange-600 hover:underline">
          Back to templates
        </button>
      </div>

      <template v-else>

        <!-- Template info card -->
        <div class="bg-white border border-gray-200 rounded-2xl p-5 mb-5 shadow-sm">
          <div class="flex items-start justify-between">
            <div>
              <h1 class="text-lg font-bold text-gray-900">{{ template.template_name }}</h1>
              <p v-if="template.description" class="text-sm text-gray-500 mt-1">{{ template.description }}</p>
            </div>
            <button
              class="text-sm text-gray-500 hover:text-orange-600 flex items-center gap-1 transition-colors"
              @click="$router.push({ name: 'template-edit', params: { name: route.params.name } })"
            >
              <Pencil class="w-3.5 h-3.5" />
              Edit
            </button>
          </div>
        </div>

        <!-- Variables form -->
        <div class="bg-white border border-gray-200 rounded-2xl p-5 mb-5 shadow-sm">
          <h2 class="text-sm font-semibold text-gray-700 mb-4">
            Fill in Variables
            <span class="font-normal text-gray-400">({{ variables.length }})</span>
          </h2>

          <p v-if="variables.length === 0" class="text-sm text-gray-400 py-4 text-center">
            This template has no variables. Click Generate to create the PDF.
          </p>

          <div v-else class="space-y-4">
            <div v-for="v in variables" :key="v">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                <span class="inline-flex items-center gap-1">
                  <span class="px-1.5 py-0.5 bg-orange-100 text-orange-700 text-xs rounded font-mono">{{ chipLabel(v) }}</span>
                </span>
              </label>
              <input
                v-model="variableValues[v]"
                type="text"
                :placeholder="`Enter value for ${v}`"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent transition"
              />
            </div>
          </div>
        </div>

        <!-- Output filename -->
        <div class="bg-white border border-gray-200 rounded-2xl p-5 mb-5 shadow-sm">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Output filename</label>
          <div class="flex items-center gap-2">
            <input
              v-model="outputFilename"
              type="text"
              placeholder="document"
              class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
            />
            <span class="text-sm text-gray-400">.pdf</span>
          </div>
        </div>

        <!-- Generate button -->
        <button
          @click="generate"
          :disabled="generating"
          class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-orange-500 text-white font-medium rounded-xl hover:bg-orange-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
        >
          <span v-if="generating" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          <FileDown v-else class="w-4 h-4" />
          {{ generating ? 'Generating PDF…' : 'Generate PDF' }}
        </button>

        <!-- Success result -->
        <div
          v-if="resultUrl"
          class="mt-4 p-4 bg-green-50 border border-green-200 rounded-xl flex items-center justify-between gap-3"
        >
          <div class="flex items-center gap-2">
            <CheckCircle class="w-5 h-5 text-green-600 flex-shrink-0" />
            <span class="text-sm text-green-800">PDF generated successfully!</span>
          </div>
          <a
            :href="resultUrl"
            :download="resultFilename"
            class="flex items-center gap-1.5 px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors flex-shrink-0"
          >
            <Download class="w-3.5 h-3.5" />
            Download
          </a>
        </div>

        <!-- Error -->
        <div v-if="errorMsg" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
          <p class="text-sm text-red-700">{{ errorMsg }}</p>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, FileDown, Pencil, CheckCircle, Download } from 'lucide-vue-next'
import { usePdfApi } from '@/composables/usePdfApi'

const route = useRoute()
const router = useRouter()
const api = usePdfApi()

const loading = ref(true)
const generating = ref(false)
const template = ref(null)
const variables = ref([])
const variableValues = reactive({})
const outputFilename = ref('')
const resultUrl = ref('')
const resultFilename = ref('')
const errorMsg = ref('')

onMounted(async () => {
  const name = route.params.name
  if (!name) { loading.value = false; return }
  try {
    const res = await api.getTemplate(name)
    if (res?.success) {
      template.value = res.data
      outputFilename.value = res.data.template_name || name
      const schema = res.data.schema || {}
      if (schema.type === 'tiptap') {
        variables.value = schema.variables || []
        variables.value.forEach(v => { variableValues[v] = '' })
      }
    }
  } finally {
    loading.value = false
  }
})

function chipLabel(name) {
  return '{{' + name + '}}'
}

async function generate() {
  errorMsg.value = ''
  resultUrl.value = ''
  resultFilename.value = ''
  generating.value = true
  try {
    const filename = (outputFilename.value.trim() || template.value?.template_name || 'document')
    const res = await api.generateHtmlPdf(
      route.params.name,
      { ...variableValues },
      filename,
    )
    if (res?.success) {
      resultUrl.value = res.data.file_url
      resultFilename.value = res.data.filename
      // Auto-trigger download
      const a = document.createElement('a')
      a.href = resultUrl.value
      a.download = resultFilename.value
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    } else {
      errorMsg.value = res?.error || 'Failed to generate PDF'
    }
  } catch (e) {
    errorMsg.value = 'Network error. Please try again.'
  } finally {
    generating.value = false
  }
}
</script>
