/**
 * Composable for managing Fabric.js overlay canvases on PDF pages.
 * Each page gets its own Fabric canvas for annotations.
 */
import { ref, shallowRef, onUnmounted } from 'vue'
import { Canvas, Rect, Textbox, Circle, Line, Path, FabricImage } from 'fabric'

export function useFabricCanvas() {
  const canvases = shallowRef(new Map()) // pageNum -> fabric.Canvas
  const activeObject = ref(null)
  const activeTool = ref('select') // select, text, highlight, draw, shape, image, whiteout, eraser

  /**
   * Initialize a Fabric canvas overlay for a specific page.
   */
  function initCanvas(pageNum, canvasEl, width, height) {
    // Destroy existing canvas for this page
    destroyCanvas(pageNum)

    const fabricCanvas = new Canvas(canvasEl, {
      width,
      height,
      selection: activeTool.value === 'select',
      isDrawingMode: activeTool.value === 'draw',
    })

    fabricCanvas.on('selection:created', (e) => {
      activeObject.value = e.selected?.[0] || null
    })

    fabricCanvas.on('selection:updated', (e) => {
      activeObject.value = e.selected?.[0] || null
    })

    fabricCanvas.on('selection:cleared', () => {
      activeObject.value = null
    })

    const newMap = new Map(canvases.value)
    newMap.set(pageNum, fabricCanvas)
    canvases.value = newMap

    return fabricCanvas
  }

  /**
   * Add a text annotation to a page.
   */
  function addText(pageNum, options = {}) {
    const canvas = canvases.value.get(pageNum)
    if (!canvas) return

    const textbox = new Textbox(options.text || 'Type here...', {
      left: options.x || 100,
      top: options.y || 100,
      width: options.width || 200,
      fontSize: options.fontSize || 16,
      fill: options.color || '#000000',
      fontFamily: options.fontFamily || 'Helvetica',
      editable: true,
    })

    canvas.add(textbox)
    canvas.setActiveObject(textbox)
    canvas.renderAll()
    return textbox
  }

  /**
   * Add a highlight rectangle to a page.
   */
  function addHighlight(pageNum, options = {}) {
    const canvas = canvases.value.get(pageNum)
    if (!canvas) return

    const rect = new Rect({
      left: options.x || 100,
      top: options.y || 100,
      width: options.width || 200,
      height: options.height || 20,
      fill: options.color || '#ffff00',
      opacity: options.opacity || 0.3,
      selectable: true,
      _annotationType: 'highlight',
    })

    canvas.add(rect)
    canvas.setActiveObject(rect)
    canvas.renderAll()
    return rect
  }

  /**
   * Add a white-out rectangle to a page.
   */
  function addWhiteout(pageNum, options = {}) {
    const canvas = canvases.value.get(pageNum)
    if (!canvas) return

    const rect = new Rect({
      left: options.x || 100,
      top: options.y || 100,
      width: options.width || 200,
      height: options.height || 30,
      fill: '#ffffff',
      opacity: 1,
      selectable: true,
      _annotationType: 'whiteout',
    })

    canvas.add(rect)
    canvas.setActiveObject(rect)
    canvas.renderAll()
    return rect
  }

  /**
   * Add a shape to a page.
   */
  function addShape(pageNum, shapeType = 'rectangle', options = {}) {
    const canvas = canvases.value.get(pageNum)
    if (!canvas) return

    let shape
    const defaults = {
      left: options.x || 100,
      top: options.y || 100,
      fill: options.fill || 'transparent',
      stroke: options.stroke || '#000000',
      strokeWidth: options.strokeWidth || 2,
      selectable: true,
    }

    if (shapeType === 'rectangle') {
      shape = new Rect({
        ...defaults,
        width: options.width || 150,
        height: options.height || 100,
        _annotationType: 'rectangle',
      })
    } else if (shapeType === 'circle') {
      shape = new Circle({
        ...defaults,
        radius: options.radius || 50,
        _annotationType: 'circle',
      })
    } else if (shapeType === 'line') {
      shape = new Line(
        [options.x || 100, options.y || 100, options.x2 || 300, options.y2 || 100],
        {
          ...defaults,
          fill: undefined,
          _annotationType: 'line',
        }
      )
    }

    if (shape) {
      canvas.add(shape)
      canvas.setActiveObject(shape)
      canvas.renderAll()
    }
    return shape
  }

  /**
   * Add an image to a page from a data URL or URL.
   */
  async function addImage(pageNum, imageSrc, options = {}) {
    const canvas = canvases.value.get(pageNum)
    if (!canvas) return

    const img = await FabricImage.fromURL(imageSrc)
    img.set({
      left: options.x || 100,
      top: options.y || 100,
      scaleX: options.scaleX || 0.5,
      scaleY: options.scaleY || 0.5,
      _annotationType: 'image',
    })

    canvas.add(img)
    canvas.setActiveObject(img)
    canvas.renderAll()
    return img
  }

  /**
   * Toggle drawing mode on a page canvas.
   */
  function setDrawingMode(pageNum, enabled, options = {}) {
    const canvas = canvases.value.get(pageNum)
    if (!canvas) return

    canvas.isDrawingMode = enabled
    if (enabled) {
      canvas.freeDrawingBrush.color = options.color || '#000000'
      canvas.freeDrawingBrush.width = options.width || 3
    }
  }

  /**
   * Delete the currently selected object.
   */
  function deleteSelected(pageNum) {
    const canvas = canvases.value.get(pageNum)
    if (!canvas) return

    const active = canvas.getActiveObject()
    if (active) {
      canvas.remove(active)
      canvas.renderAll()
      activeObject.value = null
    }
  }

  /**
   * Get all annotations from all pages in a serializable format.
   */
  function getAllAnnotations() {
    const annotations = {}
    for (const [pageNum, canvas] of canvases.value.entries()) {
      const objects = canvas.toJSON(['_annotationType']).objects
      if (objects.length > 0) {
        annotations[pageNum] = objects
      }
    }
    return annotations
  }

  /**
   * Load annotations from a serialized format.
   */
  async function loadAnnotations(annotations) {
    for (const [pageNum, objects] of Object.entries(annotations)) {
      const canvas = canvases.value.get(parseInt(pageNum))
      if (canvas && objects.length > 0) {
        await canvas.loadFromJSON({ objects, version: '6.0.0' })
        canvas.renderAll()
      }
    }
  }

  /**
   * Set the active tool (select, text, highlight, draw, shape, etc.).
   */
  function setTool(tool) {
    activeTool.value = tool

    for (const canvas of canvases.value.values()) {
      canvas.isDrawingMode = tool === 'draw'
      canvas.selection = tool === 'select'

      // Set cursor based on tool
      if (tool === 'text') {
        canvas.defaultCursor = 'text'
      } else if (tool === 'draw') {
        canvas.defaultCursor = 'crosshair'
      } else {
        canvas.defaultCursor = 'default'
      }
    }
  }

  function destroyCanvas(pageNum) {
    const canvas = canvases.value.get(pageNum)
    if (canvas) {
      canvas.dispose()
      const newMap = new Map(canvases.value)
      newMap.delete(pageNum)
      canvases.value = newMap
    }
  }

  function destroyAll() {
    for (const canvas of canvases.value.values()) {
      canvas.dispose()
    }
    canvases.value = new Map()
  }

  onUnmounted(destroyAll)

  return {
    canvases,
    activeObject,
    activeTool,
    initCanvas,
    addText,
    addHighlight,
    addWhiteout,
    addShape,
    addImage,
    setDrawingMode,
    deleteSelected,
    getAllAnnotations,
    loadAnnotations,
    setTool,
    destroyCanvas,
    destroyAll,
  }
}
