<script setup lang="ts">
import type { FitMode, NormalView, QualityPreset } from '../engine/types'

defineProps<{
  rendererEnabled: boolean
  rendererStatus: string
  fit: FitMode
  quality: QualityPreset
  normalView: NormalView
  lightAngle: number
  showBounds: boolean
  showGrid: boolean
  frameTime: number | null
  reducedMotion: boolean
  blinkEnabled: boolean
  showBlinkRegions: boolean
  leavesEnabled: boolean
  leavesCount: number
  leavesFpsCap: number
}>()

const emit = defineEmits<{
  (e: 'update:rendererEnabled', value: boolean): void
  (e: 'update:fit', value: FitMode): void
  (e: 'update:quality', value: QualityPreset): void
  (e: 'update:normalView', value: NormalView): void
  (e: 'update:lightAngle', value: number): void
  (e: 'update:showBounds', value: boolean): void
  (e: 'update:showGrid', value: boolean): void
  (e: 'update:blinkEnabled', value: boolean): void
  (e: 'update:showBlinkRegions', value: boolean): void
  (e: 'previewBlink'): void
  (e: 'update:leavesEnabled', value: boolean): void
}>()

const futureModules = ['Breathing', 'Hair Motion', 'Runtime Lighting', 'Region Overlay']
</script>

<template>
  <aside class="debug-panel" aria-label="Living Hero debug controls">
    <header><strong>DB Living Hero 2.0</strong><small>Base + Blink + Leaves + Normal test</small></header>
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
    <label>Normal view
      <select :value="normalView" :disabled="rendererStatus !== 'WebGL2'" @change="emit('update:normalView', ($event.target as HTMLSelectElement).value as NormalView)">
        <option value="base">Base</option><option value="normal">Normal map</option><option value="test-light">Test Light</option>
      </select>
    </label>
    <label v-if="normalView === 'test-light'">Light angle {{ lightAngle }}°
      <input type="range" min="0" max="359" step="1" :value="lightAngle" @input="emit('update:lightAngle', Number(($event.target as HTMLInputElement).value))" />
    </label>
    <label><input type="checkbox" :checked="showBounds" @change="emit('update:showBounds', ($event.target as HTMLInputElement).checked)" /> Artwork bounds</label>
    <label><input type="checkbox" :checked="showGrid" @change="emit('update:showGrid', ($event.target as HTMLInputElement).checked)" /> UV grid</label>
    <label><input type="checkbox" :checked="blinkEnabled && !reducedMotion && quality !== 'static' && normalView === 'base'" :disabled="reducedMotion || quality === 'static' || normalView !== 'base'"
      @change="emit('update:blinkEnabled', ($event.target as HTMLInputElement).checked)" /> Blink on/off</label>
    <button type="button" :disabled="normalView !== 'base'" @click="emit('previewBlink')">Preview Blink</button>
    <label><input type="checkbox" :checked="showBlinkRegions" @change="emit('update:showBlinkRegions', ($event.target as HTMLInputElement).checked)" /> Show Blink Regions</label>
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
