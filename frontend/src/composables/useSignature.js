/**
 * Composable for signature creation (draw, type, upload).
 */
import { ref } from 'vue'

export function useSignature() {
  const signatureDataUrl = ref(null)
  const signatureType = ref('draw') // draw, type, upload

  /**
   * Create a signature from typed text.
   */
  function createFromText(text, options = {}) {
    const canvas = document.createElement('canvas')
    canvas.width = options.width || 300
    canvas.height = options.height || 100

    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.font = `${options.fontSize || 36}px ${options.fontFamily || 'cursive'}`
    ctx.fillStyle = options.color || '#000033'
    ctx.textBaseline = 'middle'
    ctx.fillText(text, 10, canvas.height / 2)

    signatureDataUrl.value = canvas.toDataURL('image/png')
    signatureType.value = 'type'
    return signatureDataUrl.value
  }

  /**
   * Set signature from an uploaded image file.
   */
  async function createFromFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        signatureDataUrl.value = e.target.result
        signatureType.value = 'upload'
        resolve(signatureDataUrl.value)
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  /**
   * Set signature from a canvas element (drawing pad).
   */
  function createFromCanvas(canvasEl) {
    signatureDataUrl.value = canvasEl.toDataURL('image/png')
    signatureType.value = 'draw'
    return signatureDataUrl.value
  }

  function clear() {
    signatureDataUrl.value = null
  }

  return {
    signatureDataUrl,
    signatureType,
    createFromText,
    createFromFile,
    createFromCanvas,
    clear,
  }
}
