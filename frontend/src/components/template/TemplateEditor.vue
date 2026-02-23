<template>
  <div class="flex flex-col h-screen overflow-hidden bg-gray-100">

    <!-- Top bar -->
    <div class="flex items-center gap-3 px-4 py-2 bg-white border-b border-gray-200 flex-shrink-0 shadow-sm">
      <button
        class="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 transition-colors"
        @click="$router.push('/templates')"
      >
        <ArrowLeft class="w-4 h-4" />
        Templates
      </button>
      <div class="w-px h-5 bg-gray-200" />
      <input
        v-model="templateName"
        type="text"
        placeholder="Template Name"
        class="flex-1 text-base font-semibold text-gray-900 border-none outline-none bg-transparent max-w-xs placeholder-gray-400"
      />
      <div class="flex-1" />
      <span v-if="lastSaved" class="text-xs text-gray-400">Saved {{ lastSaved }}</span>
      <button
        class="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-700 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
        @click="saveTemplate"
        :disabled="saving"
      >
        <Save class="w-4 h-4" />
        {{ saving ? 'Saving…' : 'Save' }}
      </button>
      <button
        class="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50"
        @click="goGenerate"
        :disabled="!savedTemplateName"
        :title="savedTemplateName ? 'Generate PDF from this template' : 'Save first'"
      >
        <FileDown class="w-4 h-4" />
        Generate PDF
      </button>
    </div>

    <!-- Toolbar -->
    <TemplateToolbar
      v-if="editor"
      :editor="editor"
      :variables="variables"
      @add-variable="onToolbarAddVariable"
      class="flex-shrink-0"
    />

    <!-- Body -->
    <div class="flex flex-1 overflow-hidden">

      <!-- Variables sidebar -->
      <div class="w-52 bg-white border-r border-gray-200 flex flex-col flex-shrink-0">
        <div class="px-3 py-2.5 border-b border-gray-100">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Variables</p>
          <p class="text-xs text-gray-400 mt-0.5">Click to insert at cursor</p>
        </div>
        <div class="flex-1 overflow-y-auto p-3 space-y-1.5">
          <button
            v-for="v in variables"
            :key="v"
            class="w-full text-left px-2.5 py-1 text-xs bg-orange-50 text-orange-700 border border-orange-200 rounded-full hover:bg-orange-100 truncate transition-colors"
            @click="insertVariableAtCursor(v)"
            :title="'Insert ' + chipLabel(v)"
          >
            {{ chipLabel(v) }}
          </button>
          <p v-if="variables.length === 0" class="text-xs text-gray-400 text-center py-4">
            No variables yet
          </p>
        </div>
        <div class="p-3 border-t border-gray-100">
          <p class="text-xs text-gray-500 mb-1.5">Add variable</p>
          <div class="flex gap-1">
            <input
              v-model="newVarInput"
              type="text"
              placeholder="var_name"
              class="flex-1 text-xs border border-gray-200 rounded px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-orange-400 min-w-0"
              @keydown.enter="addVariable(newVarInput)"
            />
            <button
              class="px-2.5 py-1.5 text-xs bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors flex-shrink-0"
              @click="addVariable(newVarInput)"
            >+</button>
          </div>
        </div>
      </div>

      <!-- Paper viewport -->
      <div class="flex-1 overflow-auto bg-[#d9d9d9] py-8 px-6">
        <div
          class="relative mx-auto bg-white shadow-2xl"
          style="width: 794px; min-height: 1123px;"
        >
          <!-- Optional background image -->
          <img
            v-if="backgroundImage"
            :src="backgroundImage"
            class="absolute inset-0 w-full h-full object-cover pointer-events-none select-none"
            style="opacity: 0.12;"
            alt=""
          />
          <!-- TipTap content area -->
          <editor-content
            v-if="editor"
            :editor="editor"
            class="template-paper relative z-10"
            style="padding: 80px; min-height: 1123px;"
          />
        </div>
      </div>

      <!-- Right panel -->
      <div class="w-44 bg-white border-l border-gray-200 p-3 flex-shrink-0 space-y-4">
        <div>
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Page</p>
          <p class="text-xs text-gray-600">A4 · 794 × 1123 px</p>
        </div>
        <div class="border-t border-gray-100 pt-3">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Background</p>
          <button
            class="w-full text-xs px-2 py-2 border border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-orange-400 hover:text-orange-600 text-center transition-colors"
            @click="$refs.bgFileInput.click()"
          >
            {{ backgroundImage ? 'Change image' : '+ Upload image' }}
          </button>
          <input ref="bgFileInput" type="file" accept="image/*" class="hidden" @change="onBgImageChange" />
          <button
            v-if="backgroundImage"
            @click="backgroundImage = ''"
            class="mt-1.5 w-full text-xs text-red-500 hover:underline text-center"
          >Remove</button>
        </div>
        <div class="border-t border-gray-100 pt-3">
          <p class="text-xs text-gray-400">Variables: {{ variables.length }}</p>
          <p class="text-xs text-gray-400 mt-0.5">Words: {{ wordCount }}</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { TextStyle } from '@tiptap/extension-text-style'
import { Color } from '@tiptap/extension-color'
import { Underline } from '@tiptap/extension-underline'
import { TextAlign } from '@tiptap/extension-text-align'
import { FontFamily } from '@tiptap/extension-font-family'
import { Highlight } from '@tiptap/extension-highlight'
import { Image } from '@tiptap/extension-image'
import { Table, TableRow, TableCell, TableHeader } from '@tiptap/extension-table'
import { Link } from '@tiptap/extension-link'
import { ArrowLeft, Save, FileDown } from 'lucide-vue-next'
import { Variable } from './VariableNode.js'
import { FontSize } from './FontSizeExtension.js'
import TemplateToolbar from './TemplateToolbar.vue'
import { usePdfApi } from '@/composables/usePdfApi'

const router = useRouter()
const route = useRoute()
const api = usePdfApi()

const templateName = ref('Untitled Template')
const variables = ref([])
const newVarInput = ref('')
const backgroundImage = ref('')
const saving = ref(false)
const lastSaved = ref('')
const savedTemplateName = ref('')

const editor = useEditor({
  extensions: [
    StarterKit.configure({ codeBlock: false }),
    TextStyle,
    Color,
    Underline,
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    FontFamily,
    Highlight.configure({ multicolor: true }),
    Image.configure({ inline: false, allowBase64: true }),
    Table.configure({ resizable: true }),
    TableRow,
    TableCell,
    TableHeader,
    Link.configure({ openOnClick: false }),
    Variable,
    FontSize,
  ],
  content: '<p>Start typing your template here…</p>',
})

const wordCount = computed(() => {
  if (!editor.value) return 0
  const text = editor.value.getText()
  return text.trim() ? text.trim().split(/\s+/).length : 0
})

onMounted(async () => {
  const name = route.params.name
  if (name && name !== 'new') {
    savedTemplateName.value = name
    await loadTemplate(name)
  }
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

async function loadTemplate(name) {
  const res = await api.getTemplate(name)
  if (!res?.success) return
  const schema = res.data.schema || {}
  templateName.value = res.data.template_name || name
  if (schema.type === 'tiptap') {
    variables.value = schema.variables || []
    backgroundImage.value = schema.background_image || ''
    if (schema.html) {
      editor.value?.commands.setContent(schema.html)
    }
  }
}

async function saveTemplate() {
  const name = templateName.value.trim()
  if (!name) return
  saving.value = true
  try {
    const html = editor.value?.getHTML() || ''
    const schema = {
      type: 'tiptap',
      html,
      variables: variables.value,
      background_image: backgroundImage.value,
    }
    const res = await api.saveTemplate(name, schema, '', '')
    if (res?.success) {
      savedTemplateName.value = res.data.template_name
      lastSaved.value = new Date().toLocaleTimeString()
    }
  } finally {
    saving.value = false
  }
}

function insertVariableAtCursor(name) {
  editor.value?.chain().focus().insertVariable(name).run()
}

function addVariable(name) {
  name = name?.trim().replace(/[^a-zA-Z0-9_]/g, '_')
  if (!name || variables.value.includes(name)) {
    newVarInput.value = ''
    return
  }
  variables.value.push(name)
  insertVariableAtCursor(name)
  newVarInput.value = ''
}

function onToolbarAddVariable(name) {
  if (name && !variables.value.includes(name)) {
    variables.value.push(name)
  }
}

function goGenerate() {
  router.push({ name: 'template-generate', params: { name: savedTemplateName.value } })
}

function chipLabel(name) {
  return '{{' + name + '}}'
}

function onBgImageChange(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => { backgroundImage.value = ev.target.result }
  reader.readAsDataURL(file)
}
</script>

<style>
/* Paper editor styles (not scoped — needed for deep TipTap elements) */
.template-paper .ProseMirror {
  outline: none;
  min-height: 960px;
  font-size: 12pt;
  line-height: 1.6;
  color: #111827;
}
.template-paper .ProseMirror > * + * { margin-top: 0.5em; }
.template-paper .ProseMirror p { margin: 0 0 0.4em; }
.template-paper .ProseMirror h1 { font-size: 2em; font-weight: 700; margin: 0.6em 0 0.3em; }
.template-paper .ProseMirror h2 { font-size: 1.5em; font-weight: 700; margin: 0.5em 0 0.25em; }
.template-paper .ProseMirror h3 { font-size: 1.25em; font-weight: 600; margin: 0.4em 0 0.2em; }
.template-paper .ProseMirror ul { list-style: disc; padding-left: 1.5em; margin: 0.4em 0; }
.template-paper .ProseMirror ol { list-style: decimal; padding-left: 1.5em; margin: 0.4em 0; }
.template-paper .ProseMirror table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.8em 0;
}
.template-paper .ProseMirror th,
.template-paper .ProseMirror td {
  border: 1px solid #d1d5db;
  padding: 6px 10px;
  text-align: left;
  min-width: 80px;
}
.template-paper .ProseMirror th {
  background: #f9fafb;
  font-weight: 600;
}
/* Variable chip in editor */
.variable-chip {
  display: inline-block;
  background: #fed7aa;
  color: #9a3412;
  border: 1px solid #fdba74;
  border-radius: 999px;
  padding: 0 7px;
  font-size: 0.85em;
  font-weight: 500;
  user-select: none;
  cursor: default;
  white-space: nowrap;
}
</style>
