<script setup lang="ts">
import { computed, defineAsyncComponent, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import '../styles/hero.css'
const DebugPanel = defineAsyncComponent(() => import('./DebugPanel.vue'))
import BlinkLayer from './BlinkLayer.vue'
const HeroCanvas = defineAsyncComponent({
  loader: () => import('./HeroCanvas.vue'),
  onError(error, _retry, fail) { onRendererFailed(String(error)); fail() },
})
import LeavesLayer from './LeavesLayer.vue'
import type { LeafDebugView } from '../engine/animation/LeafField'
import { createHeroConfig } from '../config/hero'
import { createLightingStateForTime } from '../config/lighting'
import { skyFor } from '../config/sky'
import { moonDirectionFor } from '../config/moonlight'
import { lampWeightFor, type LampMaskView, type LampState } from '../config/lamps'
import { leafToneFor } from '../config/leafTone'
import { postFor, type PostState } from '../config/post'
import { atmosphereFor } from '../config/atmosphere'
import { layoutArtwork } from '../engine/coordinates/artwork'
import type { BreathingState } from '../engine/animation/breathing'
import type { HairState } from '../engine/animation/hair'
import { resolveQuality, qualityBudgets, lowerQuality, type DeviceHints, type ResolvedQuality } from '../engine/quality/policy'
import { TimeController, clockMinutes } from '../engine/time/TimeController'
import type { TimeSnapshot } from '../engine/time/TimeController'
import type { FitMode, LightingPresetId, LightingState, QualityPreset, RenderView } from '../engine/types'

import type { LivingHeroProps, HeroStatus } from '../types'
const props = withDefaults(defineProps<LivingHeroProps>(), { quality: 'auto', fit: 'auto', debug: false, paused: false, adaptive: true, alt: 'Autumn courtyard with a girl reading beside a stone balustrade' })
const emit = defineEmits<{
  (e: 'ready'): void; (e: 'error', reason: string): void;
  (e: 'status', status: HeroStatus): void; (e: 'time-change', time: TimeSnapshot): void;
}>()
const heroConfig = computed(() => createHeroConfig(props.assetRoot))
const loaded = ref(0)
const total = ref(16)
const posterFailed = ref(false)
const mounted = ref(false)
const inViewport = ref(true)
const pageVisible = ref(true)
const active = computed(() => mounted.value && inViewport.value && pageVisible.value && !props.paused)
const hints = ref<DeviceHints>({})
const autoBudget = ref<ResolvedQuality>('high')
const root = ref<HTMLElement | null>(null)
const rendererEnabled = ref(true)
const rendererReady = ref(false)
const rendererError = ref('')
const fit = ref<FitMode>(props.fit)
const quality = ref<QualityPreset>(props.quality)
const renderView = ref<RenderView>('lit')
const lightingMinutes = ref(clockMinutes(new Date()))
const timeMode = ref<TimeSnapshot['mode']>('realtime')
const lighting = ref<LightingState>(createLightingStateForTime(lightingMinutes.value))
const sky = computed(() => skyFor(lightingMinutes.value))
const moonDirection = computed(() => moonDirectionFor(lightingMinutes.value))
const lampsEnabled = ref(true)
const lampStrength = ref(1)
const lampMaskView = ref<LampMaskView>('none')
const lamps = computed<LampState>(() => ({ enabled: lampsEnabled.value, strength: lampStrength.value,
  weight: lampWeightFor(lightingMinutes.value), maskView: lampMaskView.value }))
const leafStyle = computed(() => {
  const tone = leafToneFor(lightingMinutes.value)
  return { filter: `brightness(${tone.brightness.toFixed(3)}) saturate(${tone.saturation.toFixed(3)})` }
})
const showBounds = ref(false)
const showGrid = ref(false)
const blinkEnabled = ref(true)
const blinkPreviewToken = ref(0)
const blinkAmount = ref(0)
const showBlinkRegions = ref(false)
const leavesEnabled = ref(true)
const leafDebugView = ref<LeafDebugView>('none')
const leavesCount = ref(0)
const breathing = ref<BreathingState>({ enabled: true, strength: 1, showRegion: false })
const hair = ref<HairState>({ enabled: true, strength: 1, showRegion: false })
const lightingDetailEnabled = ref(true)
const directionalEnabled = ref(true)
const directionalGain = ref(1)
const postEnabled = ref(true)
const bloomEnabled = ref(true)
const postView = ref<PostState['view']>('final')
const atmosphereEnabled = ref(true)
const hazeEnabled = ref(true)
const finalGradeEnabled = ref(true)
const post = computed<PostState>(() => ({ ...postFor(lightingMinutes.value), enabled: postEnabled.value,
  bloomEnabled: bloomEnabled.value, view: postView.value,
  atmosphere: { ...atmosphereFor(lightingMinutes.value), enabled: atmosphereEnabled.value,
    hazeEnabled: hazeEnabled.value, gradeEnabled: finalGradeEnabled.value } }))
const frameTime = ref<number | null>(null)
let motionQuery: MediaQueryList | null = null
const reducedMotion = ref(false)
const size = ref({ width: 1672, height: 941 })
const layout = computed(() => layoutArtwork(heroConfig.value.artwork, size.value.width, size.value.height, fit.value))
const resolvedQuality = computed(() => quality.value === 'auto' ? autoBudget.value : resolveQuality(quality.value))
const budget = computed(() => qualityBudgets[resolvedQuality.value])
const leavesConfig = computed(() => ({ ...heroConfig.value.leaves, desktopCount: budget.value.leaves, mobileCount: budget.value.mobileLeaves, dprCap: budget.value.leafDpr }))
const staticPolicy = computed(() => resolvedQuality.value === 'static')
const wantsRenderer = computed(() => rendererEnabled.value && !staticPolicy.value)
const sceneView = computed(() => renderView.value === 'base' || renderView.value === 'lit')
const leavesActive = computed(() => leavesEnabled.value && !reducedMotion.value && budget.value.motion && rendererReady.value && sceneView.value)
const blinkActive = computed(() => blinkEnabled.value && !reducedMotion.value && budget.value.motion && rendererReady.value && sceneView.value)
const breathingState = computed<BreathingState>(() => ({ ...breathing.value, enabled: breathing.value.enabled && !reducedMotion.value && budget.value.motion && wantsRenderer.value }))
const hairState = computed<HairState>(() => ({ ...hair.value, enabled: hair.value.enabled && !reducedMotion.value && budget.value.motion && wantsRenderer.value }))
const rendererStatus = computed(() => !wantsRenderer.value ? 'static' : rendererError.value ? 'fallback' : rendererReady.value ? 'WebGL2' : 'loading')
const imageStyle = computed(() => ({ left: `${layout.value.x}px`, top: `${layout.value.y}px`, width: `${layout.value.width}px`, height: `${layout.value.height}px` }))
let observer: ResizeObserver | null = null
let intersection: IntersectionObserver | null = null
const timeController = new TimeController(state => {
  emit('time-change', state)
  timeMode.value = state.mode
  lightingMinutes.value = state.minutes
  lighting.value = { ...createLightingStateForTime(state.minutes), skyEnabled: lighting.value.skyEnabled }
})

watch(wantsRenderer, () => {
  rendererReady.value = false
  frameTime.value = null
})

function onMotionChange(): void {
  reducedMotion.value = motionQuery?.matches ?? false
  if (reducedMotion.value) timeController.pause()
}

function onVisibility(): void { pageVisible.value = !document.hidden }
watch([active, wantsRenderer], () => timeController.setVisible(active.value && wantsRenderer.value))

function onRendererFailed(reason: string): void {
  rendererReady.value = false
  rendererError.value = reason
  emit('error', reason)
}

function onRendererReady(): void {
  rendererError.value = ''
  rendererReady.value = true
  emit('ready')
}

function selectLightingPreset(preset: LightingPresetId): void {
  const minutes = { dawn: 390, noon: 720, dusk: 1050, night: 1320 }[preset]
  selectLightingTime(minutes)
}

function selectLightingTime(minutes: number): void {
  timeController.select(minutes)
}

watch(() => props.quality, value => { quality.value = value })
watch(() => props.fit, value => { fit.value = value })
watch(() => props.minutes, value => value === undefined ? timeController.backToNow() : timeController.select(value))
watch(() => props.assetRoot, () => { rendererReady.value = false; rendererError.value = ''; posterFailed.value = false })
watch(quality, () => { autoBudget.value = resolveQuality('auto', hints.value) })
watch([rendererStatus, loaded, resolvedQuality], () => emit('status', {
  mode: rendererStatus.value, loaded: loaded.value, total: total.value, quality: resolvedQuality.value,
}), { immediate: true })
function onSlow(): void {
  if (props.adaptive && quality.value === 'auto') autoBudget.value = lowerQuality(autoBudget.value)
}
function retry(): void { rendererError.value = ''; rendererReady.value = false; retryToken.value++ }
const retryToken = ref(0)
defineExpose({ setTime: selectLightingTime, backToNow: () => timeController.backToNow(),
  play: () => { if (!reducedMotion.value) timeController.play() }, pause: () => timeController.pause(), retry })

onMounted(() => {
  mounted.value = true
  const nav = navigator as Navigator & { deviceMemory?: number; connection?: { saveData?: boolean } }
  hints.value = { cores: nav.hardwareConcurrency, memory: nav.deviceMemory, saveData: nav.connection?.saveData }
  autoBudget.value = resolveQuality('auto', hints.value)
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  onVisibility()
  timeController.setVisible(active.value && wantsRenderer.value)
  if (props.minutes === undefined) timeController.backToNow()
  else timeController.select(props.minutes)
  document.addEventListener('visibilitychange', onVisibility)
  onMotionChange()
  motionQuery.addEventListener('change', onMotionChange)
  observer = new ResizeObserver(([entry]) => {
    if (entry) size.value = { width: entry.contentRect.width, height: entry.contentRect.height }
  })
  if (root.value) {
    observer.observe(root.value)
    if (typeof IntersectionObserver !== 'undefined') {
      intersection = new IntersectionObserver(([entry]) => { if (entry) inViewport.value = entry.isIntersecting })
      intersection.observe(root.value)
    }
  }
})

onBeforeUnmount(() => {
  mounted.value = false
  timeController.destroy()
  document.removeEventListener('visibilitychange', onVisibility)
  observer?.disconnect()
  intersection?.disconnect()
  motionQuery?.removeEventListener('change', onMotionChange)
})
</script>

<template>
  <section ref="root" class="hero-stage" :aria-busy="rendererStatus === 'loading'" :data-quality="resolvedQuality" :data-status="rendererStatus">
    <img class="hero-image" :style="imageStyle" :src="heroConfig.artwork.baseUrl" :alt="alt" fetchpriority="high" decoding="async" @error="posterFailed = true" />
    <HeroCanvas v-if="mounted && wantsRenderer" :key="heroConfig.artwork.baseUrl + retryToken" :active="active" :artwork="heroConfig.artwork" :normal-url="heroConfig.normal.url" :sky-urls="heroConfig.sky.urls" :sky-edge-reconstruction-url="heroConfig.sky.edgeReconstructionUrl" :sky-edge-coverage-url="heroConfig.sky.edgeCoverageUrl" :hair-mask-url="heroConfig.hair.maskUrl" :material-mask-url="heroConfig.material.maskUrl" :lamp-source-url="heroConfig.lamps.sourceUrl" :lamp-influence-url="heroConfig.lamps.influenceUrl"
      :tower-receiver-url="heroConfig.architecture.towerReceiverUrl" :scene-depth-url="heroConfig.atmosphere.depthUrl" :sky="sky" :moon-direction="moonDirection" :lamps="lamps" :render-view="renderView" :lighting="lighting" :post="post" :breathing="breathingState" :hair="hairState" :blink-eyes="heroConfig.blink.eyes"
      :blink-amount="blinkActive && (renderView === 'lit' || (renderView === 'base' && hairState.enabled)) ? blinkAmount : 0" :lighting-detail-enabled="lightingDetailEnabled" :directional-strength="directionalEnabled ? directionalGain : 0" :fit="fit" :dpr-cap="budget.dpr" :max-pixels="budget.pixels"
      :class="{ 'canvas-ready': rendererReady }" @ready="onRendererReady" @failed="onRendererFailed" @frame="frameTime = $event" @slow="onSlow" @progress="loaded = $event.loaded; total = $event.total" />
    <BlinkLayer v-if="sceneView" :artwork="heroConfig.artwork" :layout="layout" :config="heroConfig.blink" :enabled="blinkActive" :active="active"
      :preview-token="blinkPreviewToken" :show-regions="showBlinkRegions" :show-patch="renderView === 'base' && !hairState.enabled" @amount="blinkAmount = $event" />
    <LeavesLayer v-if="leavesActive" :layout="layout" :key="resolvedQuality + heroConfig.artwork.baseUrl" :active="active" :config="leavesConfig" :lamp-weight="lampsEnabled ? lamps.weight * lampStrength : 0" :debug-view="leafDebugView" :style="leafStyle" @count="leavesCount = $event" />
    <div v-if="showBounds || showGrid" class="artwork-overlay" :class="{ 'show-bounds': showBounds, 'show-grid': showGrid }" :style="imageStyle" aria-hidden="true" />
    <slot v-if="rendererStatus === 'loading'" name="loading" :loaded="loaded" :total="total">
      <span class="hero-loading" role="status">Loading artwork {{ loaded }}/{{ total }}</span>
    </slot>
    <slot v-if="rendererStatus === 'fallback' || rendererStatus === 'static'" name="fallback" :reason="rendererError" :retry="retry" />
    <span v-if="posterFailed && !rendererReady" class="hero-loading" role="status">Artwork unavailable</span>
    <div class="hero-content"><slot /></div>
    <DebugPanel v-if="debug" v-model:renderer-enabled="rendererEnabled" v-model:fit="fit" v-model:quality="quality" v-model:render-view="renderView"
      v-model:lighting="lighting" v-model:lighting-detail-enabled="lightingDetailEnabled" v-model:directional-enabled="directionalEnabled" v-model:directional-gain="directionalGain" v-model:lamps-enabled="lampsEnabled" v-model:lamp-strength="lampStrength" v-model:lamp-mask-view="lampMaskView" :lamp-weight="lamps.weight" v-model:post-enabled="postEnabled" v-model:bloom-enabled="bloomEnabled" v-model:post-view="postView" :lighting-minutes="lightingMinutes" :moon-direction="moonDirection" :time-mode="timeMode" @select-lighting-preset="selectLightingPreset"
      @select-lighting-time="selectLightingTime"
      v-model:atmosphere-enabled="atmosphereEnabled" v-model:haze-enabled="hazeEnabled" v-model:final-grade-enabled="finalGradeEnabled"
      @back-to-now="timeController.backToNow()" @toggle-playback="timeMode === 'playing' ? timeController.pause() : timeController.play()"
      v-model:blink-enabled="blinkEnabled" v-model:show-blink-regions="showBlinkRegions"
      v-model:leaves-enabled="leavesEnabled" v-model:leaf-debug-view="leafDebugView" @preview-blink="blinkPreviewToken++"
      v-model:breathing="breathing"
      v-model:hair="hair"
      v-model:show-bounds="showBounds" v-model:show-grid="showGrid" :renderer-status="rendererStatus"
      :frame-time="wantsRenderer ? frameTime : null" :reduced-motion="reducedMotion" :leaves-count="leavesCount" :leaves-fps-cap="heroConfig.leaves.fpsCap" />
  </section>
</template>
