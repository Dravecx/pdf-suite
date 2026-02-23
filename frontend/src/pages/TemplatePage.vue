<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-5xl mx-auto px-6 py-10">

      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">PDF Templates</h1>
          <p class="text-gray-500 mt-1 text-sm">Design reusable templates with variables and generate PDFs instantly.</p>
        </div>
        <button
          @click="$router.push('/templates/new')"
          class="flex items-center gap-2 px-4 py-2.5 bg-orange-500 text-white rounded-xl hover:bg-orange-600 transition-colors shadow-sm font-medium"
        >
          <Plus class="w-4 h-4" />
          New Template
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-16">
        <div class="w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
      </div>

      <!-- Empty state -->
      <div
        v-else-if="templates.length === 0"
        class="text-center py-20 bg-white border border-gray-200 rounded-2xl"
      >
        <div class="w-14 h-14 bg-orange-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <LayoutTemplate class="w-7 h-7 text-orange-500" />
        </div>
        <p class="text-gray-700 font-medium">No templates yet</p>
        <p class="text-sm text-gray-400 mt-1 mb-5">Create your first template to get started.</p>
        <button
          @click="$router.push('/templates/new')"
          class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-sm"
        >
          Create Template
        </button>
      </div>

      <!-- Template grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="tmpl in templates"
          :key="tmpl.name"
          class="group bg-white border border-gray-200 rounded-2xl p-5 hover:border-orange-300 hover:shadow-md transition-all"
        >
          <!-- Icon + name -->
          <div class="flex items-start gap-3 mb-3">
            <div class="w-9 h-9 bg-orange-50 rounded-lg flex items-center justify-center flex-shrink-0">
              <FileText class="w-5 h-5 text-orange-500" />
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-900 truncate">{{ tmpl.template_name }}</h3>
              <p v-if="tmpl.description" class="text-xs text-gray-500 mt-0.5 line-clamp-2">
                {{ tmpl.description }}
              </p>
            </div>
          </div>

          <!-- Meta -->
          <p class="text-xs text-gray-400 mb-4">
            Modified {{ formatDate(tmpl.modified) }}
          </p>

          <!-- Actions -->
          <div class="flex gap-2">
            <button
              @click="$router.push({ name: 'template-edit', params: { name: tmpl.name } })"
              class="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-700 hover:border-orange-300 hover:text-orange-700 transition-colors"
            >
              <Pencil class="w-3.5 h-3.5" />
              Edit
            </button>
            <button
              @click="$router.push({ name: 'template-generate', params: { name: tmpl.name } })"
              class="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs bg-orange-50 border border-orange-200 rounded-lg text-orange-700 hover:bg-orange-100 transition-colors"
            >
              <FileDown class="w-3.5 h-3.5" />
              Generate
            </button>
            <button
              @click="confirmDelete(tmpl)"
              class="px-2.5 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-400 hover:border-red-300 hover:text-red-500 transition-colors"
              title="Delete template"
            >
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

    </div>

    <!-- Delete confirm modal -->
    <div
      v-if="deleteTarget"
      class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
      @click.self="deleteTarget = null"
    >
      <div class="bg-white rounded-2xl p-6 max-w-sm w-full shadow-xl">
        <h3 class="text-base font-semibold text-gray-900 mb-2">Delete Template?</h3>
        <p class="text-sm text-gray-600 mb-5">
          "<strong>{{ deleteTarget.template_name }}</strong>" will be permanently deleted.
        </p>
        <div class="flex gap-3">
          <button
            @click="deleteTarget = null"
            class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
          >Cancel</button>
          <button
            @click="doDelete"
            :disabled="deleting"
            class="flex-1 px-3 py-2 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600 disabled:opacity-50"
          >{{ deleting ? 'Deleting…' : 'Delete' }}</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { LayoutTemplate, Plus, FileText, Pencil, FileDown, Trash2 } from 'lucide-vue-next'
import { usePdfApi } from '@/composables/usePdfApi'

const api = usePdfApi()
const templates = ref([])
const loading = ref(true)
const deleteTarget = ref(null)
const deleting = ref(false)

onMounted(() => loadTemplates())

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

function confirmDelete(tmpl) {
  deleteTarget.value = tmpl
}

async function doDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    const res = await api.deleteTemplate(deleteTarget.value.name)
    if (res?.success) {
      deleteTarget.value = null
      await loadTemplates()
    }
  } finally {
    deleting.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>
