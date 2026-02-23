<template>
  <div class="bg-white border-b border-gray-200 px-4 py-2 flex items-center gap-1 overflow-x-auto">
    <!-- Annotation Tools -->
    <div class="flex items-center gap-1 pr-3 border-r border-gray-200">
      <ToolButton icon="MousePointer2" label="Select" tool="select" :active="activeTool" @click="setTool('select')" />
      <ToolButton icon="Type" label="Text" tool="text" :active="activeTool" @click="setTool('text')" />
      <ToolButton icon="Image" label="Image" tool="image" :active="activeTool" @click="setTool('image')" />
      <ToolButton icon="PenTool" label="Sign" tool="signature" :active="activeTool" @click="setTool('signature')" />
      <ToolButton icon="Highlighter" label="Highlight" tool="highlight" :active="activeTool" @click="setTool('highlight')" />
      <ToolButton icon="Pencil" label="Draw" tool="draw" :active="activeTool" @click="setTool('draw')" />
      <ToolButton icon="Square" label="Shape" tool="shape" :active="activeTool" @click="setTool('shape')" />
      <ToolButton icon="StickyNote" label="Note" tool="note" :active="activeTool" @click="setTool('note')" />
      <ToolButton icon="RectangleHorizontal" label="White Out" tool="whiteout" :active="activeTool" @click="setTool('whiteout')" />
      <ToolButton icon="Eraser" label="Eraser" tool="eraser" :active="activeTool" @click="setTool('eraser')" />
    </div>

    <!-- Server-side Tools -->
    <div class="flex items-center gap-1 pl-3">
      <button
        v-for="tool in serverTools"
        :key="tool.id"
        @click="$emit('server-tool', tool.id)"
        class="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
        :title="tool.label"
      >
        <component :is="tool.icon" class="w-4 h-4" />
        <span class="hidden lg:inline">{{ tool.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  MousePointer2, Type, Image, PenTool, Highlighter, Pencil,
  Square, StickyNote, RectangleHorizontal, Eraser,
  Merge, Split, Minimize2, ScanLine, FileOutput,
  Droplets, Shield, MoreHorizontal
} from 'lucide-vue-next'
import ToolButton from './ToolButton.vue'

const props = defineProps({
  activeTool: { type: String, default: 'select' },
})

const emit = defineEmits(['update:activeTool', 'server-tool'])

function setTool(tool) {
  emit('update:activeTool', tool)
}

const serverTools = [
  { id: 'merge', label: 'Merge', icon: Merge },
  { id: 'split', label: 'Split', icon: Split },
  { id: 'compress', label: 'Compress', icon: Minimize2 },
  { id: 'ocr', label: 'OCR', icon: ScanLine },
  { id: 'convert', label: 'Convert', icon: FileOutput },
  { id: 'watermark', label: 'Watermark', icon: Droplets },
  { id: 'protect', label: 'Protect', icon: Shield },
]
</script>
