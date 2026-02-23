/**
 * Composable for undo/redo using command pattern.
 */
import { ref, computed } from 'vue'

export function useUndoRedo(maxHistory = 50) {
  const undoStack = ref([])
  const redoStack = ref([])

  const canUndo = computed(() => undoStack.value.length > 0)
  const canRedo = computed(() => redoStack.value.length > 0)

  /**
   * Execute a command and push it to the undo stack.
   * Command shape: { execute: () => void, undo: () => void, description?: string }
   */
  function execute(command) {
    command.execute()
    undoStack.value.push(command)
    redoStack.value = [] // Clear redo stack on new action

    // Trim history
    if (undoStack.value.length > maxHistory) {
      undoStack.value.shift()
    }
  }

  function undo() {
    if (!canUndo.value) return

    const command = undoStack.value.pop()
    command.undo()
    redoStack.value.push(command)
  }

  function redo() {
    if (!canRedo.value) return

    const command = redoStack.value.pop()
    command.execute()
    undoStack.value.push(command)
  }

  function clear() {
    undoStack.value = []
    redoStack.value = []
  }

  return { canUndo, canRedo, execute, undo, redo, clear }
}
