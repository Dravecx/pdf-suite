<template>
  <div class="flex flex-col h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <router-link v-if="!embedded" to="/" class="text-brand-600 hover:text-brand-700">
          <FileText class="w-5 h-5" />
        </router-link>
        <span class="font-semibold text-gray-900">PDF Studio</span>

        <!-- Undo / Redo -->
        <div class="flex items-center gap-1 ml-4">
          <button
            @click="undoRedo.undo()"
            :disabled="!undoRedo.canUndo.value"
            class="p-1.5 rounded hover:bg-gray-100 disabled:opacity-30"
            title="Undo (Ctrl+Z)"
          >
            <Undo2 class="w-4 h-4" />
          </button>
          <button
            @click="undoRedo.redo()"
            :disabled="!undoRedo.canRedo.value"
            class="p-1.5 rounded hover:bg-gray-100 disabled:opacity-30"
            title="Redo (Ctrl+Y)"
          >
            <Redo2 class="w-4 h-4" />
          </button>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-500">{{ store.fileName || 'No file' }}</span>
      </div>

      <div class="flex items-center gap-2">
        <button @click="showSearch = !showSearch" class="p-2 hover:bg-gray-100 rounded" title="Search (Ctrl+F)">
          <Search class="w-4 h-4" />
        </button>
        <button @click="store.showSidebar = !store.showSidebar" class="p-2 hover:bg-gray-100 rounded" title="Toggle sidebar">
          <PanelLeft class="w-4 h-4" />
        </button>
        <button @click="store.showProperties = !store.showProperties" class="p-2 hover:bg-gray-100 rounded" title="Toggle properties">
          <PanelRight class="w-4 h-4" />
        </button>

        <!-- Export dropdown -->
        <div class="relative" ref="exportDropdown">
          <button
            @click="showExportMenu = !showExportMenu"
            class="flex items-center gap-1 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 text-sm font-medium"
          >
            <Download class="w-4 h-4" />
            Export
            <ChevronDown class="w-3 h-3" />
          </button>
          <div
            v-if="showExportMenu"
            class="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg py-1 w-48 z-20"
          >
            <button @click="exportPdf('download')" class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50">
              Download PDF
            </button>
            <button @click="exportPdf('save')" class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50">
              Save to Frappe
            </button>
            <button @click="exportPdf('flatten')" class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50">
              Flatten & Download
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toolbar -->
    <PdfToolbar
      :active-tool="store.activeTool"
      @update:active-tool="store.setTool($event)"
      @server-tool="handleServerTool"
    />

    <!-- Main area -->
    <div class="flex flex-1 overflow-hidden relative">
      <!-- Search bar -->
      <PdfSearchBar
        :visible="showSearch"
        :get-page-text="pdf.getPageText"
        :total-pages="pdf.totalPages.value"
        @close="showSearch = false"
        @go-to-page="goToPage"
      />

      <!-- Sidebar -->
      <PdfSidebar
        v-if="store.showSidebar"
        :total-pages="pdf.totalPages.value"
        :current-page="pdf.currentPage.value"
        :annotation-list="annotations.annotationList.value"
        :render-thumbnail="pdf.renderThumbnail"
        @go-to-page="goToPage"
        @select-annotation="annotations.selectAnnotation"
      />

      <!-- Canvas area -->
      <PdfCanvas
        ref="canvasArea"
        :total-pages="pdf.totalPages.value"
        :render-page="pdf.renderPage"
        :init-fabric-canvas="fabric.initCanvas"
        :scale="pdf.scale.value"
        :loading="pdf.loading.value"
        @page-changed="pdf.currentPage.value = $event"
      />

      <!-- Properties panel -->
      <PdfPropertiesPanel
        v-if="store.showProperties"
        :active-object="fabric.activeObject.value"
        :tool-options="store.toolOptions"
        @update-options="store.updateToolOptions"
        @delete-selected="fabric.deleteSelected(pdf.currentPage.value)"
      />
    </div>

    <!-- Status bar -->
    <PdfStatusBar
      :current-page="pdf.currentPage.value"
      :total-pages="pdf.totalPages.value"
      :zoom-percent="pdf.zoomPercent.value"
      :file-size="fileSizeStr"
      :is-dirty="store.isDirty"
      :last-saved="store.lastSaved"
      @zoom-in="pdf.zoomIn()"
      @zoom-out="pdf.zoomOut()"
      @zoom-fit="pdf.zoomFit()"
    />

    <!-- File drop zone (when no file loaded) -->
    <div
      v-if="pdf.totalPages.value === 0 && !pdf.loading.value"
      class="absolute inset-0 flex items-center justify-center bg-gray-50/80 z-10"
    >
      <FileDropZone
        accept=".pdf"
        label="Drop a PDF here or click to open"
        hint="Supports PDF files up to 100 MB"
        class="w-96"
        @files-selected="handleFileOpen"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  FileText, Undo2, Redo2, Search, PanelLeft, PanelRight,
  Download, ChevronDown
} from 'lucide-vue-next'
import { useEditorStore } from '@/stores/editorStore'
import { usePdfRenderer } from '@/composables/usePdfRenderer'
import { useFabricCanvas } from '@/composables/useFabricCanvas'
import { usePdfModifier } from '@/composables/usePdfModifier'
import { useUndoRedo } from '@/composables/useUndoRedo'
import { useAnnotations } from '@/composables/useAnnotations'
import { usePdfApi } from '@/composables/usePdfApi'
import PdfToolbar from './PdfToolbar.vue'
import PdfCanvas from './PdfCanvas.vue'
import PdfSidebar from './PdfSidebar.vue'
import PdfPropertiesPanel from './PdfPropertiesPanel.vue'
import PdfStatusBar from './PdfStatusBar.vue'
import PdfSearchBar from './PdfSearchBar.vue'
import FileDropZone from '@/components/shared/FileDropZone.vue'

const props = defineProps({
  embedded: { type: Boolean, default: false },
})

const route = useRoute()
const store = useEditorStore()
const pdf = usePdfRenderer()
const fabric = useFabricCanvas()
const modifier = usePdfModifier()
const undoRedo = useUndoRedo()
const annotations = useAnnotations()
const api = usePdfApi()

const canvasArea = ref(null)
const showSearch = ref(false)
const showExportMenu = ref(false)
const pdfFile = ref(null)

const fileSizeStr = computed(() => {
  if (!store.fileSize) return ''
  return humanSize(store.fileSize)
})

onMounted(() => {
  // Check for file URL in query params (iframe embed mode)
  const fileUrl = route.query.file
  if (fileUrl) {
    loadFromUrl(fileUrl)
  }

  // Check for embed mode
  if (route.query.embed === 'true') {
    const tools = route.query.tools?.split(',')
    store.setEmbedMode(tools)
  }

  // Keyboard shortcuts
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

function handleKeydown(e) {
  if (e.ctrlKey && e.key === 'z') {
    e.preventDefault()
    undoRedo.undo()
  } else if (e.ctrlKey && e.key === 'y') {
    e.preventDefault()
    undoRedo.redo()
  } else if (e.ctrlKey && e.key === 'f') {
    e.preventDefault()
    showSearch.value = !showSearch.value
  }
}

async function handleFileOpen(files) {
  if (!files.length) return
  const file = files[0]
  pdfFile.value = file
  store.setDocument('', file.name, file.size, 0)

  await pdf.loadPdf(file)
  store.totalPages = pdf.totalPages.value
}

async function loadFromUrl(url) {
  store.setDocument(url, url.split('/').pop(), 0, 0)
  await pdf.loadPdf(url)
  store.totalPages = pdf.totalPages.value
}

function goToPage(pageNum) {
  pdf.goToPage(pageNum)
  canvasArea.value?.scrollToPage(pageNum)
}

async function exportPdf(mode) {
  showExportMenu.value = false

  const source = pdfFile.value || store.fileUrl
  if (!source) return

  const pdfDoc = await modifier.loadForEdit(source)
  const allAnnots = fabric.getAllAnnotations()

  // Convert fabric annotations to pdf-lib format
  const pdfAnnotations = []
  for (const [pageNum, objects] of Object.entries(allAnnots)) {
    for (const obj of objects) {
      pdfAnnotations.push({
        page: parseInt(pageNum),
        type: obj._annotationType || obj.type,
        x: obj.left || 0,
        y: obj.top || 0,
        width: obj.width,
        height: obj.height,
        text: obj.text,
        color: obj.fill || obj.stroke,
        fontSize: obj.fontSize,
        opacity: obj.opacity,
      })
    }
  }

  if (pdfAnnotations.length > 0) {
    await modifier.embedAnnotations(pdfDoc, pdfAnnotations)
  }

  if (mode === 'download' || mode === 'flatten') {
    await modifier.downloadPdf(pdfDoc, store.fileName || 'edited.pdf')
  } else if (mode === 'save') {
    const blob = await modifier.exportAsBlob(pdfDoc)
    if (blob) {
      const file = new File([blob], store.fileName || 'edited.pdf', { type: 'application/pdf' })
      const result = await api.uploadFile(file)
      if (result.success) {
        store.markSaved(result.data.name)
      }
    }
  }
}

function handleServerTool(toolId) {
  // Will be implemented with server-side tool dialogs
  console.log('Server tool:', toolId)
}

function humanSize(bytes) {
  for (const unit of ['B', 'KB', 'MB', 'GB']) {
    if (bytes < 1024) return `${bytes.toFixed(1)} ${unit}`
    bytes /= 1024
  }
  return `${bytes.toFixed(1)} TB`
}
</script>
