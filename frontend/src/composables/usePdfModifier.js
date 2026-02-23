/**
 * Composable for modifying PDFs client-side using pdf-lib.
 * Handles annotation embedding, page operations, and export.
 */
import { ref } from 'vue'
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib'

export function usePdfModifier() {
  const exporting = ref(false)
  const exportError = ref('')

  /**
   * Load a PDF from bytes or URL for modification.
   */
  async function loadForEdit(source) {
    if (source instanceof ArrayBuffer || source instanceof Uint8Array) {
      return await PDFDocument.load(source)
    }
    if (source instanceof File) {
      const bytes = await source.arrayBuffer()
      return await PDFDocument.load(bytes)
    }
    if (typeof source === 'string') {
      const res = await fetch(source, { credentials: 'include' })
      const bytes = await res.arrayBuffer()
      return await PDFDocument.load(bytes)
    }
    throw new Error('Invalid source for PDF editing')
  }

  /**
   * Embed Fabric.js annotations into a PDF document.
   * Each annotation has: { page, type, x, y, width?, height?, text?, color?, fontSize?, imageData? }
   */
  async function embedAnnotations(pdfDoc, annotations) {
    const font = await pdfDoc.embedFont(StandardFonts.Helvetica)

    for (const annot of annotations) {
      const pageIndex = (annot.page || 1) - 1
      if (pageIndex >= pdfDoc.getPageCount()) continue

      const page = pdfDoc.getPage(pageIndex)
      const { height: pageHeight } = page.getSize()

      switch (annot.type) {
        case 'text':
          page.drawText(annot.text || '', {
            x: annot.x || 0,
            y: pageHeight - (annot.y || 0) - (annot.fontSize || 14),
            size: annot.fontSize || 14,
            font,
            color: parseColor(annot.color || '#000000'),
            opacity: annot.opacity ?? 1,
          })
          break

        case 'rectangle':
        case 'whiteout':
          page.drawRectangle({
            x: annot.x || 0,
            y: pageHeight - (annot.y || 0) - (annot.height || 20),
            width: annot.width || 100,
            height: annot.height || 20,
            color: parseColor(annot.color || (annot.type === 'whiteout' ? '#ffffff' : '#000000')),
            opacity: annot.opacity ?? 1,
            borderWidth: annot.borderWidth || 0,
          })
          break

        case 'highlight':
          page.drawRectangle({
            x: annot.x || 0,
            y: pageHeight - (annot.y || 0) - (annot.height || 14),
            width: annot.width || 100,
            height: annot.height || 14,
            color: parseColor(annot.color || '#ffff00'),
            opacity: annot.opacity ?? 0.3,
          })
          break

        case 'image':
          if (annot.imageData) {
            try {
              let image
              if (annot.imageData.startsWith('data:image/png')) {
                const base64 = annot.imageData.split(',')[1]
                image = await pdfDoc.embedPng(Uint8Array.from(atob(base64), c => c.charCodeAt(0)))
              } else {
                const base64 = annot.imageData.split(',')[1]
                image = await pdfDoc.embedJpg(Uint8Array.from(atob(base64), c => c.charCodeAt(0)))
              }
              page.drawImage(image, {
                x: annot.x || 0,
                y: pageHeight - (annot.y || 0) - (annot.height || 100),
                width: annot.width || 100,
                height: annot.height || 100,
                opacity: annot.opacity ?? 1,
              })
            } catch (e) {
              console.error('Failed to embed image annotation:', e)
            }
          }
          break

        case 'line':
          page.drawLine({
            start: { x: annot.x || 0, y: pageHeight - (annot.y || 0) },
            end: { x: annot.x2 || 100, y: pageHeight - (annot.y2 || 0) },
            thickness: annot.strokeWidth || 2,
            color: parseColor(annot.color || '#000000'),
            opacity: annot.opacity ?? 1,
          })
          break
      }
    }
  }

  /**
   * Apply page modifications (reorder, delete, rotate).
   */
  async function applyPageModifications(pdfDoc, modifications) {
    for (const mod of modifications) {
      switch (mod.type) {
        case 'rotate':
          if (mod.pageIndex < pdfDoc.getPageCount()) {
            const page = pdfDoc.getPage(mod.pageIndex)
            page.setRotation(page.getRotation().angle + (mod.angle || 90))
          }
          break
        case 'delete':
          if (mod.pageIndex < pdfDoc.getPageCount()) {
            pdfDoc.removePage(mod.pageIndex)
          }
          break
      }
    }
  }

  /**
   * Export the modified PDF as a Uint8Array.
   */
  async function exportPdf(pdfDoc) {
    exporting.value = true
    exportError.value = ''
    try {
      return await pdfDoc.save()
    } catch (e) {
      exportError.value = e.message
      return null
    } finally {
      exporting.value = false
    }
  }

  /**
   * Export as a downloadable Blob.
   */
  async function exportAsBlob(pdfDoc) {
    const bytes = await exportPdf(pdfDoc)
    if (!bytes) return null
    return new Blob([bytes], { type: 'application/pdf' })
  }

  /**
   * Trigger a download of the modified PDF.
   */
  async function downloadPdf(pdfDoc, filename = 'edited.pdf') {
    const blob = await exportAsBlob(pdfDoc)
    if (!blob) return

    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  return {
    exporting,
    exportError,
    loadForEdit,
    embedAnnotations,
    applyPageModifications,
    exportPdf,
    exportAsBlob,
    downloadPdf,
  }
}

/** Parse a hex color string into pdf-lib rgb(). */
function parseColor(hex) {
  hex = hex.replace('#', '')
  const r = parseInt(hex.substring(0, 2), 16) / 255
  const g = parseInt(hex.substring(2, 4), 16) / 255
  const b = parseInt(hex.substring(4, 6), 16) / 255
  return rgb(r, g, b)
}
