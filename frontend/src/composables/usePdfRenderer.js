/**
 * Composable for rendering PDF pages using PDF.js.
 * Handles loading, page rendering, zoom, and continuous scroll.
 */
import { ref, shallowRef, computed, onUnmounted } from 'vue'
import * as pdfjsLib from 'pdfjs-dist'

// Set worker path (PDF.js requires a web worker)
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url
).toString()

export function usePdfRenderer() {
  const pdfDoc = shallowRef(null)
  const totalPages = ref(0)
  const currentPage = ref(1)
  const scale = ref(1.0)
  const loading = ref(false)
  const error = ref('')
  const pageRendering = ref(false)
  const fileName = ref('')

  const zoomPercent = computed(() => Math.round(scale.value * 100))

  async function loadPdf(source) {
    loading.value = true
    error.value = ''

    try {
      let loadingTask

      if (source instanceof ArrayBuffer || source instanceof Uint8Array) {
        loadingTask = pdfjsLib.getDocument({ data: source })
      } else if (source instanceof File) {
        fileName.value = source.name
        const arrayBuffer = await source.arrayBuffer()
        loadingTask = pdfjsLib.getDocument({ data: arrayBuffer })
      } else if (typeof source === 'string') {
        // URL
        fileName.value = source.split('/').pop()
        loadingTask = pdfjsLib.getDocument(source)
      } else {
        throw new Error('Invalid PDF source')
      }

      const pdf = await loadingTask.promise
      pdfDoc.value = pdf
      totalPages.value = pdf.numPages
      currentPage.value = 1
    } catch (e) {
      error.value = e.message || 'Failed to load PDF'
      pdfDoc.value = null
      totalPages.value = 0
    } finally {
      loading.value = false
    }
  }

  async function renderPage(pageNum, canvas) {
    if (!pdfDoc.value || pageNum < 1 || pageNum > totalPages.value) return null

    pageRendering.value = true
    try {
      const page = await pdfDoc.value.getPage(pageNum)
      const viewport = page.getViewport({ scale: scale.value })

      canvas.width = viewport.width
      canvas.height = viewport.height

      const ctx = canvas.getContext('2d')
      const renderContext = {
        canvasContext: ctx,
        viewport,
      }

      await page.render(renderContext).promise

      return {
        width: viewport.width,
        height: viewport.height,
        originalWidth: viewport.viewBox[2],
        originalHeight: viewport.viewBox[3],
      }
    } catch (e) {
      console.error(`Error rendering page ${pageNum}:`, e)
      return null
    } finally {
      pageRendering.value = false
    }
  }

  async function renderThumbnail(pageNum, canvas, thumbScale = 0.2) {
    if (!pdfDoc.value || pageNum < 1 || pageNum > totalPages.value) return

    try {
      const page = await pdfDoc.value.getPage(pageNum)
      const viewport = page.getViewport({ scale: thumbScale })

      canvas.width = viewport.width
      canvas.height = viewport.height

      const ctx = canvas.getContext('2d')
      await page.render({ canvasContext: ctx, viewport }).promise
    } catch (e) {
      console.error(`Error rendering thumbnail ${pageNum}:`, e)
    }
  }

  async function getPageText(pageNum) {
    if (!pdfDoc.value) return ''
    const page = await pdfDoc.value.getPage(pageNum)
    const textContent = await page.getTextContent()
    return textContent.items.map(item => item.str).join(' ')
  }

  function zoomIn() {
    scale.value = Math.min(scale.value + 0.25, 5.0)
  }

  function zoomOut() {
    scale.value = Math.max(scale.value - 0.25, 0.25)
  }

  function zoomFit() {
    scale.value = 1.0
  }

  function setZoom(newScale) {
    scale.value = Math.max(0.25, Math.min(5.0, newScale))
  }

  function goToPage(pageNum) {
    currentPage.value = Math.max(1, Math.min(pageNum, totalPages.value))
  }

  function nextPage() {
    goToPage(currentPage.value + 1)
  }

  function prevPage() {
    goToPage(currentPage.value - 1)
  }

  function destroy() {
    if (pdfDoc.value) {
      pdfDoc.value.destroy()
      pdfDoc.value = null
    }
  }

  onUnmounted(destroy)

  return {
    pdfDoc,
    totalPages,
    currentPage,
    scale,
    zoomPercent,
    loading,
    error,
    pageRendering,
    fileName,
    loadPdf,
    renderPage,
    renderThumbnail,
    getPageText,
    zoomIn,
    zoomOut,
    zoomFit,
    setZoom,
    goToPage,
    nextPage,
    prevPage,
    destroy,
  }
}
