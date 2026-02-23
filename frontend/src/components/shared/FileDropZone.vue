<template>
  <div
    class="border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer"
    :class="isDragOver ? 'border-brand-500 bg-brand-50' : 'border-gray-300 hover:border-brand-400 bg-white'"
    @dragover.prevent="isDragOver = true"
    @dragleave="isDragOver = false"
    @drop.prevent="handleDrop"
    @click="openFilePicker"
  >
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      :multiple="multiple"
      class="hidden"
      @change="handleFileSelect"
    />

    <Upload class="w-12 h-12 mx-auto text-gray-400 mb-3" />
    <p class="text-gray-700 font-medium">
      {{ label || 'Drop files here or click to browse' }}
    </p>
    <p v-if="hint" class="text-sm text-gray-500 mt-1">{{ hint }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Upload } from 'lucide-vue-next'

const props = defineProps({
  accept: { type: String, default: '.pdf' },
  multiple: { type: Boolean, default: false },
  label: { type: String, default: '' },
  hint: { type: String, default: '' },
})

const emit = defineEmits(['files-selected'])

const fileInput = ref(null)
const isDragOver = ref(false)

function openFilePicker() {
  fileInput.value?.click()
}

function handleDrop(e) {
  isDragOver.value = false
  const files = Array.from(e.dataTransfer.files)
  emitFiles(files)
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files)
  emitFiles(files)
  e.target.value = '' // Reset for re-selection
}

function emitFiles(files) {
  if (!props.multiple && files.length > 1) {
    files = [files[0]]
  }
  emit('files-selected', files)
}
</script>
