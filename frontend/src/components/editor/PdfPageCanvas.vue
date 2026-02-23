<template>
  <div
    class="pdf-page-wrapper relative inline-block mb-4 shadow-lg bg-white"
    :data-page="pageNum"
  >
    <!-- PDF.js rendered canvas -->
    <canvas ref="pdfCanvas" class="block" />

    <!-- Fabric.js overlay canvas -->
    <canvas
      ref="fabricCanvas"
      class="fabric-overlay absolute top-0 left-0"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  pageNum: { type: Number, required: true },
  renderPage: { type: Function, required: true },
  initFabricCanvas: { type: Function, default: null },
  scale: { type: Number, default: 1.0 },
})

const emit = defineEmits(['page-rendered', 'page-visible'])

const pdfCanvas = ref(null)
const fabricCanvas = ref(null)

async function render() {
  if (!pdfCanvas.value) return

  const result = await props.renderPage(props.pageNum, pdfCanvas.value)
  if (!result) return

  // Initialize Fabric.js overlay with same dimensions
  if (props.initFabricCanvas && fabricCanvas.value) {
    props.initFabricCanvas(props.pageNum, fabricCanvas.value, result.width, result.height)
  }

  emit('page-rendered', {
    pageNum: props.pageNum,
    width: result.width,
    height: result.height,
  })
}

onMounted(render)

// Re-render when scale changes
watch(() => props.scale, render)
</script>
