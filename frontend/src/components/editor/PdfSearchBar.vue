<template>
  <div v-if="visible" class="absolute top-2 right-4 z-10 bg-white border border-gray-200 rounded-lg shadow-lg p-3 flex items-center gap-2">
    <Search class="w-4 h-4 text-gray-400" />
    <input
      ref="searchInput"
      v-model="query"
      @keydown.enter="findNext"
      @keydown.escape="$emit('close')"
      type="text"
      placeholder="Search in document..."
      class="w-56 text-sm border-none outline-none"
    />
    <span v-if="total > 0" class="text-xs text-gray-500">{{ current }} / {{ total }}</span>
    <button @click="findPrev" class="p-1 hover:bg-gray-100 rounded" :disabled="total === 0">
      <ChevronUp class="w-4 h-4" />
    </button>
    <button @click="findNext" class="p-1 hover:bg-gray-100 rounded" :disabled="total === 0">
      <ChevronDown class="w-4 h-4" />
    </button>
    <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded">
      <X class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { Search, ChevronUp, ChevronDown, X } from 'lucide-vue-next'

const props = defineProps({
  visible: { type: Boolean, default: false },
  getPageText: { type: Function, default: null },
  totalPages: { type: Number, default: 0 },
})

const emit = defineEmits(['close', 'go-to-page'])

const searchInput = ref(null)
const query = ref('')
const results = ref([])
const current = ref(0)
const total = ref(0)

watch(() => props.visible, async (v) => {
  if (v) {
    await nextTick()
    searchInput.value?.focus()
  }
})

watch(query, async (q) => {
  if (!q || !props.getPageText) {
    results.value = []
    current.value = 0
    total.value = 0
    return
  }

  const matches = []
  for (let i = 1; i <= props.totalPages; i++) {
    const text = await props.getPageText(i)
    if (text.toLowerCase().includes(q.toLowerCase())) {
      matches.push(i)
    }
  }
  results.value = matches
  total.value = matches.length
  current.value = matches.length > 0 ? 1 : 0
})

function findNext() {
  if (total.value === 0) return
  current.value = current.value >= total.value ? 1 : current.value + 1
  emit('go-to-page', results.value[current.value - 1])
}

function findPrev() {
  if (total.value === 0) return
  current.value = current.value <= 1 ? total.value : current.value - 1
  emit('go-to-page', results.value[current.value - 1])
}
</script>
