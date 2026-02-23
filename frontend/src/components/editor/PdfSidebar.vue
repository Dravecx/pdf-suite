<template>
  <div class="w-52 bg-white border-r border-gray-200 flex flex-col h-full">
    <!-- Tabs -->
    <div class="flex border-b border-gray-200">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="flex-1 py-2 px-1 text-xs font-medium transition-colors border-b-2"
        :class="activeTab === tab.id
          ? 'border-brand-500 text-brand-600'
          : 'border-transparent text-gray-500 hover:text-gray-700'"
      >
        <component :is="tab.icon" class="w-4 h-4 mx-auto" />
      </button>
    </div>

    <!-- Thumbnails -->
    <div v-if="activeTab === 'thumbnails'" class="flex-1 overflow-y-auto p-2 space-y-2">
      <div
        v-for="page in totalPages"
        :key="page"
        @click="$emit('go-to-page', page)"
        class="cursor-pointer rounded-lg border-2 transition-colors p-1"
        :class="currentPage === page ? 'border-brand-500 bg-brand-50' : 'border-gray-200 hover:border-brand-300'"
      >
        <canvas
          :ref="el => { if (el) thumbnailRefs[page] = el }"
          class="w-full bg-white rounded"
        />
        <p class="text-xs text-center text-gray-500 mt-1">{{ page }}</p>
      </div>
    </div>

    <!-- Annotations list -->
    <div v-if="activeTab === 'annotations'" class="flex-1 overflow-y-auto p-2">
      <div v-if="annotationList.length === 0" class="text-sm text-gray-500 text-center py-4">
        No annotations yet
      </div>
      <div
        v-for="annot in annotationList"
        :key="annot.id"
        class="px-3 py-2 text-xs border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
        @click="$emit('select-annotation', annot)"
      >
        <div class="flex items-center justify-between">
          <span class="font-medium capitalize">{{ annot.type }}</span>
          <span class="text-gray-400">p.{{ annot.page }}</span>
        </div>
        <p v-if="annot.text" class="text-gray-500 truncate mt-0.5">{{ annot.text }}</p>
      </div>
    </div>

    <!-- Outline (placeholder) -->
    <div v-if="activeTab === 'outline'" class="flex-1 overflow-y-auto p-2">
      <p class="text-sm text-gray-500 text-center py-4">Document outline</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { LayoutGrid, List, FileText } from 'lucide-vue-next'

const props = defineProps({
  totalPages: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  annotationList: { type: Array, default: () => [] },
  renderThumbnail: { type: Function, default: null },
})

defineEmits(['go-to-page', 'select-annotation'])

const activeTab = ref('thumbnails')
const thumbnailRefs = reactive({})

const tabs = [
  { id: 'thumbnails', icon: LayoutGrid },
  { id: 'annotations', icon: List },
  { id: 'outline', icon: FileText },
]

// Render thumbnails when they become available
watch(() => props.totalPages, async (pages) => {
  if (pages && props.renderThumbnail) {
    // Wait for refs to be set
    await new Promise(r => setTimeout(r, 100))
    for (let i = 1; i <= pages; i++) {
      const canvas = thumbnailRefs[i]
      if (canvas) {
        await props.renderThumbnail(i, canvas, 0.2)
      }
    }
  }
})
</script>
