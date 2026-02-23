<template>
  <div class="bg-gray-100 border-t border-gray-200 px-4 py-1.5 flex items-center justify-between text-xs text-gray-600">
    <!-- Left: Page info -->
    <div class="flex items-center gap-4">
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
    </div>

    <!-- Center: Zoom -->
    <div class="flex items-center gap-2">
      <button @click="$emit('zoom-out')" class="p-1 hover:bg-gray-200 rounded" title="Zoom out">
        <ZoomOut class="w-3.5 h-3.5" />
      </button>
      <span class="w-12 text-center">{{ zoomPercent }}%</span>
      <button @click="$emit('zoom-in')" class="p-1 hover:bg-gray-200 rounded" title="Zoom in">
        <ZoomIn class="w-3.5 h-3.5" />
      </button>
      <button @click="$emit('zoom-fit')" class="p-1 hover:bg-gray-200 rounded ml-1" title="Fit to page">
        <Maximize2 class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Right: File info + save status -->
    <div class="flex items-center gap-4">
      <span v-if="fileSize">{{ fileSize }}</span>
      <span v-if="isDirty" class="text-amber-600">Unsaved changes</span>
      <span v-else-if="lastSaved" class="text-green-600">Saved</span>
    </div>
  </div>
</template>

<script setup>
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-vue-next'

defineProps({
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 0 },
  zoomPercent: { type: Number, default: 100 },
  fileSize: { type: String, default: '' },
  isDirty: { type: Boolean, default: false },
  lastSaved: { type: String, default: '' },
})

defineEmits(['zoom-in', 'zoom-out', 'zoom-fit'])
</script>
