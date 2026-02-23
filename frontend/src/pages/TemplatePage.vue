<template>
  <div class="max-w-4xl mx-auto px-6 py-12">
    <h1 class="text-2xl font-bold text-gray-900 mb-2">PDF Templates</h1>
    <p class="text-gray-600 mb-8">Design and generate PDFs from reusable templates.</p>

    <!-- Template list -->
    <div v-if="loading" class="text-center py-12">
      <div class="w-8 h-8 border-3 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto" />
    </div>

    <div v-else-if="templates.length === 0" class="text-center py-12 bg-white border border-gray-200 rounded-xl">
      <LayoutTemplate class="w-12 h-12 mx-auto text-gray-400 mb-3" />
      <p class="text-gray-600">No templates yet</p>
      <p class="text-sm text-gray-500 mt-1">Create your first template to get started.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="template in templates"
        :key="template.name"
        class="bg-white border border-gray-200 rounded-xl p-5 hover:border-brand-300 transition-colors"
      >
        <h3 class="font-medium text-gray-900">{{ template.template_name }}</h3>
        <p v-if="template.description" class="text-sm text-gray-500 mt-1 line-clamp-2">{{ template.description }}</p>
        <p class="text-xs text-gray-400 mt-3">Modified: {{ template.modified }}</p>
        <div class="flex gap-2 mt-3">
          <button @click="deleteTemplate(template.name)" class="text-xs text-red-500 hover:underline">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { LayoutTemplate } from 'lucide-vue-next'
import { usePdfApi } from '@/composables/usePdfApi'

const api = usePdfApi()
const templates = ref([])
const loading = ref(true)

onMounted(async () => {
  await loadTemplates()
})

async function loadTemplates() {
  loading.value = true
  try {
    const res = await api.listTemplates()
    if (res?.success) {
      templates.value = res.data.templates || []
    }
  } finally {
    loading.value = false
  }
}

async function deleteTemplate(name) {
  const res = await api.deleteTemplate(name)
  if (res?.success) {
    await loadTemplates()
  }
}
</script>
