<template>
  <div
    ref="canvasContainer"
    class="flex-1 overflow-auto bg-gray-300 flex flex-col items-center py-6 px-4"
    @scroll="onScroll"
  >
    <PdfPageCanvas
      v-for="page in totalPages"
      :key="page"
      :page-num="page"
      :render-page="renderPage"
      :init-fabric-canvas="initFabricCanvas"
      :scale="scale"
      @page-rendered="onPageRendered"
    />

    <!-- Empty state -->
    <div v-if="totalPages === 0 && !loading" class="text-center py-20">
      <FileText class="w-16 h-16 mx-auto text-gray-400 mb-4" />
      <p class="text-gray-500 text-lg">No PDF loaded</p>
      <p class="text-gray-400 text-sm mt-1">Open a file to start editing</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-20">
      <div class="w-8 h-8 border-3 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto" />
      <p class="text-gray-500 mt-3">Loading PDF...</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FileText } from 'lucide-vue-next'
import PdfPageCanvas from './PdfPageCanvas.vue'

const props = defineProps({
  totalPages: { type: Number, default: 0 },
  renderPage: { type: Function, required: true },
  initFabricCanvas: { type: Function, default: null },
  scale: { type: Number, default: 1.0 },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['page-changed', 'page-rendered'])

const canvasContainer = ref(null)

function onScroll() {
  if (!canvasContainer.value) return

  const container = canvasContainer.value
  const pages = container.querySelectorAll('.pdf-page-wrapper')
  const containerTop = container.scrollTop
  const containerHeight = container.clientHeight

  let currentPage = 1
  for (const page of pages) {
    const pageTop = page.offsetTop - container.offsetTop
    const pageBottom = pageTop + page.clientHeight

    if (pageTop <= containerTop + containerHeight / 2 && pageBottom > containerTop) {
      currentPage = parseInt(page.dataset.page)
    }
  }

  emit('page-changed', currentPage)
}

function scrollToPage(pageNum) {
  const container = canvasContainer.value
  if (!container) return

  const page = container.querySelector(`[data-page="${pageNum}"]`)
  if (page) {
    page.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

function onPageRendered(data) {
  emit('page-rendered', data)
}

defineExpose({ scrollToPage })
</script>
