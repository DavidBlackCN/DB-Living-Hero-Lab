<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import UiIcon from './UiIcon.vue'
const props = defineProps<{ modelValue: string; label: string; options: { value: string; label: string }[] }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
const open = ref(false)
const root = ref<HTMLElement>()
const trigger = ref<HTMLButtonElement>()
const selected = computed(() => props.options.find(o => o.value === props.modelValue)?.label)
async function show() {
  open.value = !open.value
  if (open.value) { await nextTick(); root.value?.querySelector<HTMLButtonElement>('[aria-checked="true"]')?.focus() }
}
function close(focus = false) { open.value = false; if (focus) trigger.value?.focus() }
function choose(value: string) { emit('update:modelValue', value); close(true) }
function outside(e: PointerEvent) { if (!root.value?.contains(e.target as Node)) close() }
function keys(e: KeyboardEvent) {
  if (e.key === 'Escape' && open.value) { e.stopPropagation(); close(true) }
  if (!open.value || !['ArrowDown','ArrowUp','Home','End'].includes(e.key)) return
  e.preventDefault()
  const buttons = Array.from(root.value!.querySelectorAll<HTMLButtonElement>('[role="menuitemradio"]'))
  const i = buttons.indexOf(document.activeElement as HTMLButtonElement)
  buttons[e.key === 'Home' ? 0 : e.key === 'End' ? buttons.length - 1 : (i + (e.key === 'ArrowDown' ? 1 : -1) + buttons.length) % buttons.length]?.focus()
}
onMounted(() => document.addEventListener('pointerdown', outside))
onBeforeUnmount(() => document.removeEventListener('pointerdown', outside))
</script>
<template>
 <div ref="root" class="themed-select" @keydown="keys" @focusout="e => { if (!$el.contains(e.relatedTarget)) close() }">
  <button ref="trigger" type="button" :aria-label="label" aria-haspopup="menu" :aria-expanded="open" @click="show"><span>{{ selected }}</span><UiIcon name="chevron" :class="{ 'select-open': open }" /></button>
  <Transition name="panel"><div v-if="open" class="select-options" role="menu" :aria-label="label"><button v-for="option in options" :key="option.value" role="menuitemradio" :aria-checked="modelValue === option.value" @click="choose(option.value)"><span>{{ option.label }}</span><span aria-hidden="true">{{ modelValue === option.value ? '✓' : '' }}</span></button></div></Transition>
 </div>
</template>
