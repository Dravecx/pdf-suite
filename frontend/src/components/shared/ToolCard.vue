<template>
  <router-link
    :to="route"
    class="bg-white border border-gray-200 rounded-xl p-5 hover:border-brand-300 hover:shadow-md transition-all group"
  >
    <div
      class="w-10 h-10 rounded-lg flex items-center justify-center mb-3"
      :class="bgClass"
    >
      <component :is="icon" class="w-5 h-5" :class="iconClass" />
    </div>
    <h3 class="font-semibold text-gray-900 group-hover:text-brand-600 transition-colors">
      {{ title }}
    </h3>
    <p class="text-sm text-gray-500 mt-1">{{ description }}</p>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: { type: [Object, Function], required: true },
  title: { type: String, required: true },
  description: { type: String, default: '' },
  route: { type: String, required: true },
  color: { type: String, default: 'brand' },
})

const colorMap = {
  brand: { bg: 'bg-purple-100', icon: 'text-purple-600' },
  blue: { bg: 'bg-blue-100', icon: 'text-blue-600' },
  green: { bg: 'bg-green-100', icon: 'text-green-600' },
  amber: { bg: 'bg-amber-100', icon: 'text-amber-600' },
  red: { bg: 'bg-red-100', icon: 'text-red-600' },
  purple: { bg: 'bg-purple-100', icon: 'text-purple-600' },
  indigo: { bg: 'bg-indigo-100', icon: 'text-indigo-600' },
}

const bgClass = computed(() => colorMap[props.color]?.bg || 'bg-gray-100')
const iconClass = computed(() => colorMap[props.color]?.icon || 'text-gray-600')
</script>
