<template>
  <PdfEditor :embedded="isEmbedded" />
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import PdfEditor from '@/components/editor/PdfEditor.vue'

const route = useRoute()
const isEmbedded = computed(() => route.query.embed === 'true')

onMounted(() => {
  // Pick up file passed from StudioHome
  if (window.__pdfStudioFile) {
    // PdfEditor will handle file loading via its drop zone or we trigger it
    const file = window.__pdfStudioFile
    delete window.__pdfStudioFile

    // Dispatch a custom event that PdfEditor can listen to
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('pdf-studio-open-file', { detail: file }))
    }, 100)
  }
})
</script>
