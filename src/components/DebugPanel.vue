<script setup lang="ts">
import { formatLightingTime, lightingPresets } from '../config/lighting'
import type { FitMode, LightingPresetId, LightingState, QualityPreset, RenderView, RGBColor } from '../engine/types'

const props = defineProps<{
  rendererEnabled: boolean
  rendererStatus: string
  fit: FitMode
  quality: QualityPreset
  renderView: RenderView
  lighting: LightingState
  lightingMinutes: number
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
  (e: 'update:renderView', value: RenderView): void
  (e: 'update:lighting', value: LightingState): void
  (e: 'selectLightingPreset', value: LightingPresetId): void
  (e: 'selectLightingTime', value: number): void
  (e: 'update:showBounds', value: boolean): void
  (e: 'update:showGrid', value: boolean): void
  (e: 'update:blinkEnabled', value: boolean): void
  (e: 'update:showBlinkRegions', value: boolean): void
  (e: 'previewBlink'): void
  (e: 'update:leavesEnabled', value: boolean): void
}>()

const futureModules = ['Breathing', 'Hair Motion', 'Region Overlay']

function updateLighting(patch: Partial<LightingState>): void {
  emit('update:lighting', { ...props.lighting, ...patch })
}

function rgbToHex(color: RGBColor): string {
  return `#${[color.r, color.g, color.b].map(value => Math.round(value * 255).toString(16).padStart(2, '0')).join('')}`
}

function hexToRgb(value: string): RGBColor {
  return { r: parseInt(value.slice(1, 3), 16) / 255, g: parseInt(value.slice(3, 5), 16) / 255, b: parseInt(value.slice(5, 7), 16) / 255 }
}

function directionAngle(direction: LightingState['direction']): number {
  return (Math.round(Math.atan2(direction.y, direction.x) * 180 / Math.PI) + 360) % 360
}

function directionElevation(direction: LightingState['direction']): number {
  return Math.round(Math.asin(direction.z / Math.hypot(direction.x, direction.y, direction.z)) * 180 / Math.PI)
}

function withDirection(angle: number, elevation: number): LightingState['direction'] {
  const azimuth = angle * Math.PI / 180
  const altitude = elevation * Math.PI / 180
  const planar = Math.cos(altitude)
  return { x: Math.cos(azimuth) * planar, y: Math.sin(azimuth) * planar, z: Math.sin(altitude) }
}
</script>

<template>
  <aside class="debug-panel" aria-label="Living Hero debug controls">
    <header><strong>DB Living Hero 2.0</strong><small>Base + Blink + Leaves + Runtime Lighting</small></header>
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
    <label>Render view
      <select :value="renderView" :disabled="rendererStatus !== 'WebGL2'" @change="emit('update:renderView', ($event.target as HTMLSelectElement).value as RenderView)">
        <option value="base">Base</option><option value="normal">Normal</option><option value="lit">Lit</option>
      </select>
    </label>
    <details class="lighting-controls" open>
      <summary>Runtime Lighting</summary>
      <label class="range-control time-control"><span>24H Preview <output>{{ formatLightingTime(lightingMinutes) }}</output></span>
        <input type="range" min="0" max="1440" step="1" :value="lightingMinutes"
          :aria-valuetext="formatLightingTime(lightingMinutes)"
          @input="emit('selectLightingTime', Number(($event.target as HTMLInputElement).value))" />
        <div class="time-ticks" aria-hidden="true"><span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>24:00</span></div>
      </label>
      <div class="lighting-time-shortcuts" role="group" aria-label="Time calibration points">
        <button v-for="preset in Object.values(lightingPresets)" :key="preset.id" type="button"
          :aria-pressed="lightingMinutes === preset.minutes" @click="emit('selectLightingPreset', preset.id)">{{ preset.label }}</button>
      </div>
      <label><input type="checkbox" :checked="lighting.enabled" @change="updateLighting({ enabled: ($event.target as HTMLInputElement).checked })" /> Lighting on/off</label>
      <label class="range-control">Exposure {{ lighting.exposure.toFixed(2) }}
        <input type="range" min="0.65" max="1.1" step="0.01" :value="lighting.exposure"
          @input="updateLighting({ exposure: Number(($event.target as HTMLInputElement).value) })" />
      </label>
      <label class="range-control">Relight {{ lighting.relightStrength.toFixed(2) }}
        <input type="range" min="0" max="1" step="0.01" :value="lighting.relightStrength"
          @input="updateLighting({ relightStrength: Number(($event.target as HTMLInputElement).value) })" />
      </label>
      <label class="range-control">Direction {{ directionAngle(lighting.direction) }}°
        <input type="range" min="0" max="359" step="1" :value="directionAngle(lighting.direction)"
          @input="updateLighting({ direction: withDirection(Number(($event.target as HTMLInputElement).value), directionElevation(lighting.direction)) })" />
      </label>
      <label class="range-control">Elevation {{ directionElevation(lighting.direction) }}°
        <input type="range" min="10" max="85" step="1" :value="directionElevation(lighting.direction)"
          @input="updateLighting({ direction: withDirection(directionAngle(lighting.direction), Number(($event.target as HTMLInputElement).value)) })" />
      </label>
      <label class="range-control">Key light {{ lighting.intensity.toFixed(2) }}
        <input type="range" min="0" max="1.2" step="0.01" :value="lighting.intensity"
          @input="updateLighting({ intensity: Number(($event.target as HTMLInputElement).value) })" />
      </label>
      <label class="range-control">Ambient {{ lighting.ambientIntensity.toFixed(3) }}
        <input type="range" min="0" max="0.8" step="0.005" :value="lighting.ambientIntensity"
          @input="updateLighting({ ambientIntensity: Number(($event.target as HTMLInputElement).value) })" />
      </label>
      <label>Key color <input type="color" :value="rgbToHex(lighting.color)" @input="updateLighting({ color: hexToRgb(($event.target as HTMLInputElement).value) })" /></label>
      <label>Ambient color <input type="color" :value="rgbToHex(lighting.ambientColor)" @input="updateLighting({ ambientColor: hexToRgb(($event.target as HTMLInputElement).value) })" /></label>
    </details>
    <label><input type="checkbox" :checked="showBounds" @change="emit('update:showBounds', ($event.target as HTMLInputElement).checked)" /> Artwork bounds</label>
    <label><input type="checkbox" :checked="showGrid" @change="emit('update:showGrid', ($event.target as HTMLInputElement).checked)" /> UV grid</label>
    <label><input type="checkbox" :checked="blinkEnabled && !reducedMotion && quality !== 'static' && renderView === 'base'" :disabled="reducedMotion || quality === 'static' || renderView !== 'base'"
      @change="emit('update:blinkEnabled', ($event.target as HTMLInputElement).checked)" /> Blink on/off</label>
    <button type="button" :disabled="renderView !== 'base'" @click="emit('previewBlink')">Preview Blink</button>
    <label><input type="checkbox" :checked="showBlinkRegions" @change="emit('update:showBlinkRegions', ($event.target as HTMLInputElement).checked)" /> Show Blink Regions</label>
    <label :title="renderView !== 'base' ? 'Available in Base view' : reducedMotion ? 'Disabled by reduced motion' : quality === 'static' ? 'Disabled by Static quality' : 'Toggle drifting leaves'">
      <input type="checkbox" :checked="leavesEnabled && !reducedMotion && quality !== 'static' && renderView === 'base'" :disabled="renderView !== 'base' || reducedMotion || quality === 'static'"
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
