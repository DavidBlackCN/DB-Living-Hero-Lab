<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { LeafField } from '../engine/animation/LeafField'
import type { LeafConfig } from '../engine/animation/LeafField'
import type { ArtworkLayout } from '../engine/coordinates/artwork'

const props = defineProps<{ layout: ArtworkLayout; config: LeafConfig }>()
const emit = defineEmits<{ (e: 'count', count: number): void }>()
const canvas = ref<HTMLCanvasElement | null>(null)
let field: LeafField | null = null

onMounted(() => {
  if (!canvas.value) return
  try {
    field = new LeafField(canvas.value, props.config, props.layout, count => emit('count', count))
    void field.start()
  } catch (error) {
    console.warn('Living Hero leaves unavailable:', error)
    emit('count', 0)
  }
})

watch(() => props.layout, layout => field?.updateLayout(layout))

onBeforeUnmount(() => {
  field?.destroy()
  field = null
})
</script>

<template>
  <canvas ref="canvas" class="leaves-canvas" aria-hidden="true" />
</template>
