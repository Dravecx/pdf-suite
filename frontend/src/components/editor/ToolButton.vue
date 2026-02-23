<template>
  <button
    @click="$emit('click')"
    class="p-2 rounded-md transition-colors"
    :class="active === tool ? 'bg-brand-100 text-brand-700' : 'text-gray-600 hover:bg-gray-100'"
    :title="label"
  >
    <component :is="iconComponent" class="w-4 h-4" />
  </button>
</template>

<script setup>
import { computed } from 'vue'
import * as icons from 'lucide-vue-next'

const props = defineProps({
  icon: { type: String, required: true },
  label: { type: String, default: '' },
  tool: { type: String, default: '' },
  active: { type: String, default: '' },
})

defineEmits(['click'])

const iconComponent = computed(() => icons[props.icon] || icons.Circle)
</script>
