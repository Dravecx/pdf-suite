<template>
  <div class="toolbar bg-white border-b border-gray-200 px-3 py-1.5 flex items-center flex-wrap gap-1 select-none">

    <!-- Undo / Redo -->
    <div class="toolbar-group">
      <ToolBtn title="Undo (Ctrl+Z)" :disabled="!editor.can().undo()" @click="editor.chain().focus().undo().run()">
        <Undo class="w-4 h-4" />
      </ToolBtn>
      <ToolBtn title="Redo (Ctrl+Y)" :disabled="!editor.can().redo()" @click="editor.chain().focus().redo().run()">
        <Redo class="w-4 h-4" />
      </ToolBtn>
    </div>

    <div class="toolbar-sep" />

    <!-- Heading / Paragraph -->
    <select
      :value="currentHeading"
      @change="setHeading($event.target.value)"
      class="toolbar-select w-28"
      title="Paragraph style"
    >
      <option value="paragraph">Normal</option>
      <option value="1">Heading 1</option>
      <option value="2">Heading 2</option>
      <option value="3">Heading 3</option>
    </select>

    <div class="toolbar-sep" />

    <!-- Font family -->
    <select
      :value="currentFont"
      @change="editor.chain().focus().setFontFamily($event.target.value).run()"
      class="toolbar-select w-32"
      title="Font family"
    >
      <option v-for="f in fonts" :key="f.value" :value="f.value">{{ f.label }}</option>
    </select>

    <!-- Font size -->
    <select
      :value="currentFontSize"
      @change="editor.chain().focus().setFontSize($event.target.value).run()"
      class="toolbar-select w-14"
      title="Font size"
    >
      <option v-for="s in fontSizes" :key="s" :value="s">{{ s }}</option>
    </select>

    <div class="toolbar-sep" />

    <!-- Bold / Italic / Underline / Strike -->
    <ToolBtn title="Bold (Ctrl+B)" :active="editor.isActive('bold')" @click="editor.chain().focus().toggleBold().run()">
      <Bold class="w-4 h-4" />
    </ToolBtn>
    <ToolBtn title="Italic (Ctrl+I)" :active="editor.isActive('italic')" @click="editor.chain().focus().toggleItalic().run()">
      <Italic class="w-4 h-4" />
    </ToolBtn>
    <ToolBtn title="Underline (Ctrl+U)" :active="editor.isActive('underline')" @click="editor.chain().focus().toggleUnderline().run()">
      <UnderlineIcon class="w-4 h-4" />
    </ToolBtn>
    <ToolBtn title="Strikethrough" :active="editor.isActive('strike')" @click="editor.chain().focus().toggleStrike().run()">
      <Strikethrough class="w-4 h-4" />
    </ToolBtn>

    <div class="toolbar-sep" />

    <!-- Text color -->
    <div class="relative" title="Text color">
      <ToolBtn class="relative" @click="showColorPicker = !showColorPicker">
        <span class="flex flex-col items-center gap-0.5">
          <Baseline class="w-4 h-4" />
          <span class="w-4 h-1 rounded-sm" :style="{ background: currentColor }"></span>
        </span>
      </ToolBtn>
      <div v-if="showColorPicker" class="color-picker-popup">
        <div class="grid grid-cols-8 gap-1 p-2">
          <button
            v-for="c in colors" :key="c"
            class="w-5 h-5 rounded border border-gray-200 hover:scale-110 transition-transform"
            :style="{ background: c }"
            @click="applyColor(c)"
          />
        </div>
        <button class="w-full text-xs text-center py-1 border-t border-gray-100 text-gray-500 hover:text-gray-700" @click="editor.chain().focus().unsetColor().run(); showColorPicker=false">Remove color</button>
      </div>
    </div>

    <!-- Highlight -->
    <div class="relative" title="Highlight">
      <ToolBtn :active="editor.isActive('highlight')" @click="showHighlightPicker = !showHighlightPicker">
        <span class="flex flex-col items-center gap-0.5">
          <Highlighter class="w-4 h-4" />
          <span class="w-4 h-1 rounded-sm" :style="{ background: currentHighlight }"></span>
        </span>
      </ToolBtn>
      <div v-if="showHighlightPicker" class="color-picker-popup">
        <div class="grid grid-cols-5 gap-1 p-2">
          <button
            v-for="c in highlights" :key="c"
            class="w-6 h-6 rounded border border-gray-200 hover:scale-110 transition-transform"
            :style="{ background: c }"
            @click="applyHighlight(c)"
          />
        </div>
        <button class="w-full text-xs text-center py-1 border-t border-gray-100 text-gray-500 hover:text-gray-700" @click="editor.chain().focus().unsetHighlight().run(); showHighlightPicker=false">Remove highlight</button>
      </div>
    </div>

    <div class="toolbar-sep" />

    <!-- Alignment -->
    <ToolBtn title="Align left" :active="editor.isActive({textAlign:'left'})" @click="editor.chain().focus().setTextAlign('left').run()">
      <AlignLeft class="w-4 h-4" />
    </ToolBtn>
    <ToolBtn title="Align center" :active="editor.isActive({textAlign:'center'})" @click="editor.chain().focus().setTextAlign('center').run()">
      <AlignCenter class="w-4 h-4" />
    </ToolBtn>
    <ToolBtn title="Align right" :active="editor.isActive({textAlign:'right'})" @click="editor.chain().focus().setTextAlign('right').run()">
      <AlignRight class="w-4 h-4" />
    </ToolBtn>
    <ToolBtn title="Justify" :active="editor.isActive({textAlign:'justify'})" @click="editor.chain().focus().setTextAlign('justify').run()">
      <AlignJustify class="w-4 h-4" />
    </ToolBtn>

    <div class="toolbar-sep" />

    <!-- Lists -->
    <ToolBtn title="Bullet list" :active="editor.isActive('bulletList')" @click="editor.chain().focus().toggleBulletList().run()">
      <List class="w-4 h-4" />
    </ToolBtn>
    <ToolBtn title="Numbered list" :active="editor.isActive('orderedList')" @click="editor.chain().focus().toggleOrderedList().run()">
      <ListOrdered class="w-4 h-4" />
    </ToolBtn>

    <div class="toolbar-sep" />

    <!-- Table -->
    <ToolBtn title="Insert table" @click="insertTable">
      <Table2 class="w-4 h-4" />
    </ToolBtn>

    <!-- Image -->
    <ToolBtn title="Insert image" @click="insertImage">
      <ImageIcon class="w-4 h-4" />
    </ToolBtn>

    <div class="toolbar-sep" />

    <!-- Variable -->
    <div class="relative">
      <button
        class="flex items-center gap-1.5 px-2 py-1 text-xs font-medium bg-orange-50 text-orange-700 border border-orange-200 rounded hover:bg-orange-100 transition-colors"
        @click="showVarInput = !showVarInput"
        title="Insert variable"
      >
        <Braces class="w-3.5 h-3.5" />
        Insert Variable
      </button>
      <div v-if="showVarInput" class="var-popup" @keydown.esc="showVarInput=false">
        <p class="text-xs text-gray-500 mb-2">Select or type a variable name</p>
        <div class="flex flex-wrap gap-1 mb-2">
          <button
            v-for="v in variables" :key="v"
            class="px-2 py-0.5 text-xs bg-orange-100 text-orange-800 rounded-full hover:bg-orange-200"
            @click="doInsertVariable(v)"
          >{{ chipLabel(v) }}</button>
        </div>
        <div class="flex gap-1">
          <input
            v-model="newVarName"
            type="text"
            placeholder="variable_name"
            class="flex-1 text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-orange-400"
            @keydown.enter="doInsertVariable(newVarName)"
            @keydown.esc="showVarInput=false"
          />
          <button
            class="px-2 py-1 text-xs bg-orange-500 text-white rounded hover:bg-orange-600"
            @click="doInsertVariable(newVarName)"
          >Insert</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, defineComponent, h } from 'vue'
import {
  Undo, Redo, Bold, Italic, Strikethrough,
  AlignLeft, AlignCenter, AlignRight, AlignJustify,
  List, ListOrdered, Table2, Image as ImageIcon,
  Baseline, Highlighter, Braces,
} from 'lucide-vue-next'
import { Underline as UnderlineIcon } from 'lucide-vue-next'

// ToolBtn defined in setup scope so it's automatically available in the template
const ToolBtn = defineComponent({
  props: { active: Boolean, disabled: Boolean, title: String },
  emits: ['click'],
  setup(props, { slots, emit }) {
    return () =>
      h('button', {
        title: props.title,
        disabled: props.disabled,
        onClick: (e) => { e.preventDefault(); emit('click') },
        class: [
          'toolbar-btn',
          props.active ? 'toolbar-btn-active' : '',
          props.disabled ? 'opacity-40 cursor-not-allowed' : '',
        ].join(' '),
      }, slots.default?.())
  },
})

const props = defineProps({
  editor: { type: Object, required: true },
  variables: { type: Array, default: () => [] },
})

const emit = defineEmits(['add-variable'])

const showColorPicker = ref(false)
const showHighlightPicker = ref(false)
const showVarInput = ref(false)
const newVarName = ref('')
const currentColor = ref('#000000')
const currentHighlight = ref('#fef08a')

const fonts = [
  { label: 'Arial', value: 'Arial, sans-serif' },
  { label: 'Times New Roman', value: "'Times New Roman', serif" },
  { label: 'Calibri', value: 'Calibri, sans-serif' },
  { label: 'Georgia', value: 'Georgia, serif' },
  { label: 'Courier New', value: "'Courier New', monospace" },
  { label: 'Helvetica', value: 'Helvetica, sans-serif' },
]

const fontSizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 72]

const colors = [
  '#000000','#1a1a1a','#374151','#6B7280','#9CA3AF','#D1D5DB','#F3F4F6','#ffffff',
  '#dc2626','#ea580c','#d97706','#16a34a','#0284c7','#7c3aed','#db2777','#0f766e',
  '#fca5a5','#fdba74','#fde68a','#86efac','#93c5fd','#c4b5fd','#f9a8d4','#99f6e4',
]

const highlights = ['#fef08a','#bbf7d0','#bfdbfe','#fecaca','#e9d5ff','#fed7aa','#f0fdf4','#fffbeb']

const currentHeading = computed(() => {
  for (let i = 1; i <= 3; i++) {
    if (props.editor.isActive('heading', { level: i })) return String(i)
  }
  return 'paragraph'
})

const currentFont = computed(() => {
  return props.editor.getAttributes('textStyle').fontFamily || 'Arial, sans-serif'
})

const currentFontSize = computed(() => {
  return props.editor.getAttributes('textStyle').fontSize || '12'
})

function setHeading(val) {
  if (val === 'paragraph') {
    props.editor.chain().focus().setParagraph().run()
  } else {
    props.editor.chain().focus().toggleHeading({ level: parseInt(val) }).run()
  }
}

function applyColor(c) {
  currentColor.value = c
  props.editor.chain().focus().setColor(c).run()
  showColorPicker.value = false
}

function applyHighlight(c) {
  currentHighlight.value = c
  props.editor.chain().focus().setHighlight({ color: c }).run()
  showHighlightPicker.value = false
}

function insertTable() {
  props.editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
}

function insertImage() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      props.editor.chain().focus().setImage({ src: ev.target.result }).run()
    }
    reader.readAsDataURL(file)
  }
  input.click()
}

function doInsertVariable(name) {
  name = name?.trim().replace(/[^a-zA-Z0-9_]/g, '_')
  if (!name) return
  props.editor.chain().focus().insertVariable(name).run()
  emit('add-variable', name)
  newVarName.value = ''
  showVarInput.value = false
}

function chipLabel(name) {
  return '{{' + name + '}}'
}

// Close popups on outside click
function onDocClick(e) {
  if (!e.target.closest('.toolbar')) {
    showColorPicker.value = false
    showHighlightPicker.value = false
    showVarInput.value = false
  }
}

onMounted(() => document.addEventListener('click', onDocClick))
onUnmounted(() => document.removeEventListener('click', onDocClick))
</script>

<style scoped>
.toolbar-group { @apply flex items-center gap-0.5; }
.toolbar-sep { @apply w-px h-5 bg-gray-200 mx-1; }

:deep(.toolbar-btn) {
  @apply flex items-center justify-center w-7 h-7 rounded text-gray-700 hover:bg-gray-100 transition-colors;
}
:deep(.toolbar-btn-active) {
  @apply bg-blue-50 text-blue-700 hover:bg-blue-100;
}
.toolbar-select {
  @apply text-xs border border-gray-200 rounded px-1.5 py-1 bg-white text-gray-700 focus:outline-none focus:ring-1 focus:ring-blue-400;
}
.color-picker-popup {
  @apply absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-max;
}
.var-popup {
  @apply absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 p-3 w-64;
}
</style>
