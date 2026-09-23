<script setup lang="ts">
import type { FitMode, QualityPreset } from '../engine/types'

defineProps<{
  rendererEnabled: boolean
  rendererStatus: string
  fit: FitMode
  quality: QualityPreset
  showBounds: boolean
  showGrid: boolean
  frameTime: number | null
  reducedMotion: boolean
  previewBlink: boolean
  leavesEnabled: boolean
  leavesCount: number
  leavesFpsCap: number
}>()

const emit = defineEmits<{
  (e: 'update:rendererEnabled', value: boolean): void
  (e: 'update:fit', value: FitMode): void
  (e: 'update:quality', value: QualityPreset): void
  (e: 'update:showBounds', value: boolean): void
  (e: 'update:showGrid', value: boolean): void
  (e: 'update:previewBlink', value: boolean): void
  (e: 'update:leavesEnabled', value: boolean): void
}>()

const futureModules = ['Blink', 'Breathing', 'Hair Motion', 'Runtime Lighting', 'Region Overlay']
</script>

<template>
  <aside class="debug-panel" aria-label="Living Hero debug controls">
    <header><strong>DB Living Hero 2.0</strong><small>Base + Leaves preview</small></header>
    <label><input type="checkbox" :checked="rendererEnabled" @change="emit('update:rendererEnabled', ($event.target as HTMLInputElement).checked)" /> Renderer</label>
    <label>Fit
      <select :value="fit" @change="emit('update:fit', ($event.target as HTMLSelectElement).value as FitMode)">
        <option value="auto">Auto</option><option value="cover">Cover</option><option value="contain">Contain</option>
      </select>
    </label>
    <label>Quality
      <select :value="quality" @change="emit('update:quality', ($event.target as HTMLSelectElement).value as QualityPreset)">
        <option value="auto">Auto</option><option value="balanced">Balanced</option><option value="static">Static</option>
      </select>
    </label>
    <label><input type="checkbox" :checked="showBounds" @change="emit('update:showBounds', ($event.target as HTMLInputElement).checked)" /> Artwork bounds</label>
    <label><input type="checkbox" :checked="showGrid" @change="emit('update:showGrid', ($event.target as HTMLInputElement).checked)" /> UV grid</label>
    <label title="Static candidate preview, not a blink animation"><input type="checkbox" :checked="previewBlink" @change="emit('update:previewBlink', ($event.target as HTMLInputElement).checked)" /> Preview closed-eye candidate</label>
    <label :title="reducedMotion ? 'Disabled by reduced motion' : quality === 'static' ? 'Disabled by Static quality' : 'Toggle drifting leaves'">
      <input type="checkbox" :checked="leavesEnabled && !reducedMotion && quality !== 'static'" :disabled="reducedMotion || quality === 'static'"
        @change="emit('update:leavesEnabled', ($event.target as HTMLInputElement).checked)" /> Leaves <small>{{ leavesCount }} active</small>
    </label>
    <div class="debug-future" aria-label="Future modules">
      <label v-for="name in futureModules" :key="name" :title="`${name}: Not implemented`">
        <input type="checkbox" disabled /> {{ name }} <small>Not implemented</small>
      </label>
    </div>
    <footer>
      <div>Mode: {{ rendererStatus }}</div>
      <div>Motion: {{ reducedMotion ? 'reduced' : 'normal' }}</div>
      <div>Base frame: {{ frameTime === null ? 'idle' : `${frameTime.toFixed(1)} ms (on demand)` }}</div>
      <div>Leaves: {{ leavesCount ? `≤ ${leavesFpsCap} FPS` : 'off' }}</div>
    </footer>
  </aside>
</template>
