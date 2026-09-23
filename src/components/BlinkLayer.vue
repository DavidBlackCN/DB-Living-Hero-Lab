<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { BlinkTimeline, type BlinkConfig } from '../engine/animation/BlinkTimeline'
import type { ArtworkLayout } from '../engine/coordinates/artwork'
import type { ArtworkSpec } from '../engine/types'

const props = defineProps<{
  artwork: ArtworkSpec
  layout: ArtworkLayout
  config: BlinkConfig
  enabled: boolean
  previewToken: number
  showRegions: boolean
}>()

const closed = ref(false)
const scale = computed(() => props.layout.width / props.artwork.width)
const eyeStyles = computed(() => props.config.eyes.map(eye => ({
  left: `${props.layout.x + eye.x * scale.value}px`,
  top: `${props.layout.y + eye.y * scale.value}px`,
  width: `${eye.width * scale.value}px`,
  height: `${eye.height * scale.value}px`,
})))
let timeline: BlinkTimeline | null = null

function onVisibility(): void {
  timeline?.setVisible(!document.hidden)
}

onMounted(() => {
  timeline = new BlinkTimeline(props.config, value => { closed.value = value })
  timeline.setVisible(!document.hidden)
  timeline.setEnabled(props.enabled)
  document.addEventListener('visibilitychange', onVisibility)
})

watch(() => props.enabled, value => timeline?.setEnabled(value))
watch(() => props.previewToken, () => timeline?.preview())

onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', onVisibility)
  timeline?.destroy()
  timeline = null
})
</script>

<template>
  <div class="blink-layer" aria-hidden="true">
    <template v-for="(eye, index) in config.eyes" :key="eye.url">
      <img class="blink-eye" :class="{ 'is-closed': closed }" :src="eye.url" :style="eyeStyles[index]" alt="" />
      <div v-if="showRegions" class="blink-region" :style="eyeStyles[index]" />
    </template>
  </div>
</template>
