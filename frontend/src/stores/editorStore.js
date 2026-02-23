/**
 * Pinia store for PDF editor state.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useEditorStore = defineStore('editor', () => {
  // Document state
  const fileUrl = ref('')
  const fileName = ref('')
  const fileSize = ref(0)
  const totalPages = ref(0)
  const currentPage = ref(1)

  // View state
  const scale = ref(1.0)
  const sidebarTab = ref('thumbnails') // thumbnails, outline, annotations, layers
  const showSidebar = ref(true)
  const showProperties = ref(false)

  // Tool state
  const activeTool = ref('select')
  const toolOptions = ref({
    color: '#000000',
    fontSize: 16,
    fontFamily: 'Helvetica',
    strokeWidth: 2,
    opacity: 1,
    highlightColor: '#ffff00',
  })

  // Editing state
  const isDirty = ref(false)
  const sessionName = ref(null)
  const lastSaved = ref(null)

  // Embed mode (when loaded in iframe)
  const isEmbedded = ref(false)
  const allowedTools = ref(null) // null = all tools, or array of tool names

  const zoomPercent = computed(() => Math.round(scale.value * 100))

  function setDocument(url, name, size, pages) {
    fileUrl.value = url
    fileName.value = name
    fileSize.value = size
    totalPages.value = pages
    currentPage.value = 1
    isDirty.value = false
    sessionName.value = null
    lastSaved.value = null
  }

  function setTool(tool) {
    activeTool.value = tool
  }

  function updateToolOptions(opts) {
    toolOptions.value = { ...toolOptions.value, ...opts }
  }

  function markDirty() {
    isDirty.value = true
  }

  function markSaved(name) {
    isDirty.value = false
    sessionName.value = name
    lastSaved.value = new Date().toISOString()
  }

  function setEmbedMode(tools = null) {
    isEmbedded.value = true
    allowedTools.value = tools
  }

  function reset() {
    fileUrl.value = ''
    fileName.value = ''
    fileSize.value = 0
    totalPages.value = 0
    currentPage.value = 1
    scale.value = 1.0
    activeTool.value = 'select'
    isDirty.value = false
    sessionName.value = null
    lastSaved.value = null
  }

  return {
    fileUrl,
    fileName,
    fileSize,
    totalPages,
    currentPage,
    scale,
    zoomPercent,
    sidebarTab,
    showSidebar,
    showProperties,
    activeTool,
    toolOptions,
    isDirty,
    sessionName,
    lastSaved,
    isEmbedded,
    allowedTools,
    setDocument,
    setTool,
    updateToolOptions,
    markDirty,
    markSaved,
    setEmbedMode,
    reset,
  }
})
