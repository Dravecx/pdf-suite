/**
 * Composable for managing annotation state across pages.
 */
import { ref, computed } from 'vue'

export function useAnnotations() {
  const annotations = ref({}) // { pageNum: [annotationObjects] }
  const selectedAnnotation = ref(null)

  const annotationCount = computed(() => {
    return Object.values(annotations.value).reduce((sum, page) => sum + page.length, 0)
  })

  const annotationList = computed(() => {
    const list = []
    for (const [page, annots] of Object.entries(annotations.value)) {
      for (const annot of annots) {
        list.push({ ...annot, page: parseInt(page) })
      }
    }
    return list.sort((a, b) => a.page - b.page)
  })

  function addAnnotation(pageNum, annotation) {
    if (!annotations.value[pageNum]) {
      annotations.value[pageNum] = []
    }
    annotation.id = annotation.id || generateId()
    annotations.value[pageNum].push(annotation)
    return annotation
  }

  function removeAnnotation(pageNum, annotationId) {
    if (!annotations.value[pageNum]) return
    annotations.value[pageNum] = annotations.value[pageNum].filter(a => a.id !== annotationId)
    if (annotations.value[pageNum].length === 0) {
      delete annotations.value[pageNum]
    }
  }

  function updateAnnotation(pageNum, annotationId, updates) {
    if (!annotations.value[pageNum]) return
    const idx = annotations.value[pageNum].findIndex(a => a.id === annotationId)
    if (idx >= 0) {
      annotations.value[pageNum][idx] = { ...annotations.value[pageNum][idx], ...updates }
    }
  }

  function clearPage(pageNum) {
    delete annotations.value[pageNum]
  }

  function clearAll() {
    annotations.value = {}
    selectedAnnotation.value = null
  }

  function selectAnnotation(annotation) {
    selectedAnnotation.value = annotation
  }

  function generateId() {
    return `annot_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`
  }

  return {
    annotations,
    selectedAnnotation,
    annotationCount,
    annotationList,
    addAnnotation,
    removeAnnotation,
    updateAnnotation,
    clearPage,
    clearAll,
    selectAnnotation,
  }
}
