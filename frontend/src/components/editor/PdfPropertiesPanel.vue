<template>
  <div class="w-56 bg-white border-l border-gray-200 p-4 overflow-y-auto">
    <h3 class="text-sm font-semibold text-gray-900 mb-4">Properties</h3>

    <div v-if="!activeObject" class="text-sm text-gray-500">
      Select an annotation to edit its properties.
    </div>

    <div v-else class="space-y-4">
      <!-- Color -->
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Color</label>
        <input
          type="color"
          :value="toolOptions.color"
          @input="$emit('update-options', { color: $event.target.value })"
          class="w-full h-8 rounded border border-gray-300 cursor-pointer"
        />
      </div>

      <!-- Font Size -->
      <div v-if="activeObject?.type === 'textbox'">
        <label class="block text-xs font-medium text-gray-600 mb-1">Font Size</label>
        <input
          type="number"
          :value="toolOptions.fontSize"
          @input="$emit('update-options', { fontSize: parseInt($event.target.value) })"
          min="8"
          max="120"
          class="w-full px-3 py-1.5 border border-gray-300 rounded text-sm"
        />
      </div>

      <!-- Opacity -->
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">
          Opacity: {{ Math.round(toolOptions.opacity * 100) }}%
        </label>
        <input
          type="range"
          :value="toolOptions.opacity"
          @input="$emit('update-options', { opacity: parseFloat($event.target.value) })"
          min="0"
          max="1"
          step="0.05"
          class="w-full"
        />
      </div>

      <!-- Stroke Width -->
      <div v-if="['rect', 'circle', 'line', 'path'].includes(activeObject?.type)">
        <label class="block text-xs font-medium text-gray-600 mb-1">Stroke Width</label>
        <input
          type="number"
          :value="toolOptions.strokeWidth"
          @input="$emit('update-options', { strokeWidth: parseInt($event.target.value) })"
          min="1"
          max="20"
          class="w-full px-3 py-1.5 border border-gray-300 rounded text-sm"
        />
      </div>

      <!-- Delete -->
      <button
        @click="$emit('delete-selected')"
        class="w-full px-3 py-2 text-sm text-red-600 bg-red-50 hover:bg-red-100 rounded-md transition-colors"
      >
        Delete
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  activeObject: { type: Object, default: null },
  toolOptions: { type: Object, default: () => ({}) },
})

defineEmits(['update-options', 'delete-selected'])
</script>
