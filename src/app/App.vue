<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import ThemedSelect from './ThemedSelect.vue'
import UiIcon from './UiIcon.vue'
import LivingHero from '../components/LivingHero.vue'
import type { HeroAdjustments, LivingHeroHandle, TimeSnapshot } from '../index'
import type { QualityPreset, RenderView } from '../engine/types'
import { postFor } from '../config/post'
import { createLightingStateForTime } from '../config/lighting'
import './homepage.css'

const hero = ref<LivingHeroHandle | null>(null)
const sceneTime = ref<TimeSnapshot>({ mode: 'realtime', minutes: 720 })
const now = ref<Date | null>(null)
const immersive = ref(false)
const fullscreen = ref(false)
const motion = ref(true)
const reduced = ref(false)
const view = ref<RenderView>('lit')
const quality = ref<QualityPreset>('auto')
const manual = ref<HeroAdjustments | undefined>()
const menuOpen = ref(false)
const detailsOpen = ref(false)
const keyboardNavigation = ref(false)
const detailsButton = ref<HTMLButtonElement | null>(null)
const settingsButton = ref<HTMLButtonElement | null>(null)
const notice = ref('')
let timer: ReturnType<typeof setInterval> | undefined
let media: MediaQueryList | undefined
const presets = [{ name: '晨曦', minutes: 390 }, { name: '白昼', minutes: 720 }, { name: '薄暮', minutes: 1050 }, { name: '夜色', minutes: 1320 }]
const formatTime = (m: number) => `${String(Math.floor(m / 60) % 24).padStart(2, '0')}:${String(Math.floor(m % 60)).padStart(2, '0')}`
const greeting = computed(() => { const h = now.value?.getHours() ?? 18; return `${h < 6 ? 'STILL AWAKE' : h < 12 ? 'GOOD MORNING' : h < 18 ? 'GOOD AFTERNOON' : 'GOOD NIGHT'}, NICE TO MEET YOU` })
const clock = computed(() => now.value ? formatTime(now.value.getHours() * 60 + now.value.getMinutes()) : '—:—')
const date = computed(() => now.value ? new Intl.DateTimeFormat('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' }).format(now.value) : '正在同步时间')
const period = computed(() => { const m = sceneTime.value.minutes; return m < 300 || m >= 1140 ? '夜色' : m < 480 ? '晨曦' : m < 990 ? '白昼' : '薄暮' })
const values = computed(() => {
  const post = postFor(sceneTime.value.minutes)
  return { exposureOffset: 0, bloomStrength: post.bloomStrength, threshold: post.threshold, saturation: post.saturation,
    directionalStrength: 1, bandSoftness: createLightingStateForTime(sceneTime.value.minutes).bandSoftness, ...manual.value }
})
const controls: { key: keyof HeroAdjustments; label: string; min: number; max: number; step: number; unit: string }[] = [
  { key: 'exposureOffset', label: '曝光补偿', min: -1, max: 1, step: .01, unit: ' EV' },
  { key: 'bloomStrength', label: '泛光强度', min: 0, max: .5, step: .005, unit: '' },
  { key: 'threshold', label: '高亮阈值', min: .1, max: 1, step: .01, unit: '' },
  { key: 'directionalStrength', label: '方向明暗', min: 0, max: 1.5, step: .01, unit: '×' },
  { key: 'bandSoftness', label: '边缘柔和', min: .1, max: .65, step: .01, unit: '' },
  { key: 'saturation', label: '色彩饱和', min: .6, max: 1.3, step: .01, unit: '×' },
]
function adjust(key: keyof HeroAdjustments, event: Event): void {
  manual.value = { ...values.value, [key]: Number((event.target as HTMLInputElement).value) }
}
function closeMenu(): void { menuOpen.value = false; detailsOpen.value = false; settingsButton.value?.focus() }
function outside(event: PointerEvent): void { keyboardNavigation.value = false; if (!(event.target as Element)?.closest('.control-dock,.dock-toggle')) { menuOpen.value = false; detailsOpen.value = false } }
async function toggleFullscreen(): Promise<void> {
  try { if (document.fullscreenElement) await document.exitFullscreen(); else await document.documentElement.requestFullscreen() }
  catch { notice.value = '浏览器暂不支持全屏，仍可使用沉浸模式。' }
}
function fullChanged(): void { fullscreen.value = !!document.fullscreenElement }
function preference(): void { reduced.value = media?.matches ?? false; if (reduced.value) { motion.value = false; hero.value?.pause() } }
function tick(): void { now.value = new Date() }
function visibility(): void {
  clearInterval(timer)
  if (!document.hidden) { tick(); timer = setInterval(tick, 1000) }
}
function keys(event: KeyboardEvent): void {
  keyboardNavigation.value = true
  if (event.key === 'Escape') { if (detailsOpen.value) { detailsOpen.value = false; detailsButton.value?.focus() } else if (menuOpen.value) closeMenu(); else immersive.value = false }
  if (event.key === 'Escape') return
  if (event.ctrlKey || event.metaKey || event.altKey || event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement || (event.target as HTMLElement)?.isContentEditable) return
  if (event.key.toLowerCase() === 'h') immersive.value = !immersive.value

}
onMounted(() => {
  media = matchMedia('(prefers-reduced-motion: reduce)'); preference(); visibility()
  media.addEventListener('change', preference)
  document.addEventListener('visibilitychange', visibility)
  document.addEventListener('fullscreenchange', fullChanged)
  window.addEventListener('keydown', keys)
  document.addEventListener('pointerdown', outside)
})
onBeforeUnmount(() => {
  clearInterval(timer); media?.removeEventListener('change', preference)
  document.removeEventListener('visibilitychange', visibility); document.removeEventListener('fullscreenchange', fullChanged)
  window.removeEventListener('keydown', keys)
  document.removeEventListener('pointerdown', outside)
})
</script>

<template>
  <main class="dream-page" :class="{ 'is-immersive': immersive, 'keyboard-navigation': keyboardNavigation }">
    <LivingHero ref="hero" class="dream-art" entrance :motion="motion" :view="view" :quality="quality" :adjustments="manual" @time-change="sceneTime = $event">
      <template #loading="{ loaded, total }"><div class="arrival-status" role="status">光影正在醒来 <progress :value="loaded" :max="total" aria-label="场景加载进度" /></div></template>
      <template #fallback="{ reason, retry }"><div v-if="reason" class="arrival-status" role="status">已显示静态原画 <button @click="retry">重试</button></div></template>
    </LivingHero>
    <div class="frame-line" aria-hidden="true" />
    <header class="dream-header interface">
      <button class="wordmark" type="button" aria-label="黑姐姐 · Living Hero"><UiIcon name="sparkle" /> 黑姐姐 <small>DAVIDBLACKCN</small></button>
      <div class="top-actions"><span class="live-tag"><i />{{ sceneTime.mode === 'realtime' ? '与此刻同频' : '时光预览' }}</span><button class="icon-button" :aria-label="fullscreen ? '退出全屏' : '进入全屏'" @click="toggleFullscreen"><UiIcon name="fullscreen" /></button></div>
    </header>
    <section class="clock-block interface" aria-label="本地实时时钟">
      <p class="eyebrow greeting"><i aria-hidden="true" />{{ greeting }}</p>
      <time class="clock" :datetime="now?.toISOString()">{{ clock }}</time>
      <div class="date-line"><span>{{ date }}</span><span class="date-rule" /><span>{{ now?.getFullYear() ?? '—' }}</span></div>
      <div class="profile"><h1>黑姐姐 <small>DavidBlackCN</small></h1><p class="profile-role">Developer · Blogger · INFJ-T</p><p class="profile-intro">欢迎来到黑姐姐の驿站。<br />这里记录代码、文字与折腾过程，<br />也收藏那些值得慢下来观察的事物。</p><figure class="profile-motto"><span class="quote-mark" aria-hidden="true">“</span><blockquote>有些事你不要太当真。</blockquote><figcaption><span />《售梦者》</figcaption></figure><nav class="social-links" aria-label="社交平台（展示占位，无跳转）"><button v-for="social in [{name:'github',label:'GitHub'},{name:'bilibili',label:'BiliBili'},{name:'mail',label:'Email'},{name:'qq',label:'QQ'}]" :key="social.name" :aria-label="social.label + '（暂无链接）'" :title="social.label + ' · 暂无链接'"><UiIcon :name="social.name" /></button></nav></div>
    </section>
    <aside class="scene-caption interface"><span />秋日回廊<small>让时光，慢慢经过。</small></aside>
    <Transition name="panel"><section v-if="menuOpen" id="scene-controls" class="control-dock interface" aria-label="场景控制">
      <div class="dock-heading"><div class="period-name"><UiIcon :name="period === '夜色' ? 'moon' : period === '白昼' ? 'sun' : 'twilight'" />{{ period }}</div><output>{{ formatTime(sceneTime.minutes) }}</output><button class="sync-button" :disabled="sceneTime.mode === 'realtime'" @click="hero?.backToNow()"><UiIcon name="sync" /> {{ sceneTime.mode === 'realtime' ? '已同步' : '回到此刻' }}</button></div>
      <input class="timeline" type="range" aria-label="24 小时光照预览" :aria-valuetext="formatTime(sceneTime.minutes)" min="0" max="1440" step="1" :value="sceneTime.minutes" @input="hero?.setTime(Number(($event.target as HTMLInputElement).value))" />
      <div class="time-ticks" aria-hidden="true"><span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>24:00</span></div>
      <div class="dock-bottom"><div class="presets"><button v-for="preset in presets" :key="preset.name" :aria-pressed="Math.abs(sceneTime.minutes - preset.minutes) < 1" @click="hero?.setTime(preset.minutes)">{{ preset.name }}</button></div><div class="playback"><button :disabled="reduced" :aria-label="sceneTime.mode === 'playing' ? '暂停昼夜轮播' : '播放昼夜轮播'" @click="sceneTime.mode === 'playing' ? hero?.pause() : hero?.play()"><UiIcon :name="sceneTime.mode === 'playing' ? 'pause' : 'play'" /></button><span /><button :disabled="reduced" :aria-pressed="motion && !reduced" @click="motion = !motion"><UiIcon name="sparkle" /> {{ reduced ? '静态' : motion ? '动效开' : '动效关' }}</button></div></div>
      <div class="settings-heading"><span>光影调节</span><small>{{ manual ? '手动' : '自动' }} · EV {{ values.exposureOffset.toFixed(2) }}</small><button ref="detailsButton" class="settings-launch" :aria-expanded="detailsOpen" aria-controls="light-details" :aria-label="detailsOpen ? '收起光影参数' : '展开光影参数'" @click="detailsOpen = !detailsOpen">{{ detailsOpen ? '−' : '＋' }}</button></div>
      <Transition name="details"><div v-if="detailsOpen" id="light-details" class="light-details">
        <div class="settings-mode"><span>拖动参数进入手动模式</span><button @click="manual = manual ? undefined : { ...values }">{{ manual ? '恢复昼夜自动' : '固定当前值' }}</button></div>
        <fieldset :disabled="view !== 'lit'"><legend class="sr-only">光影参数</legend><label v-for="control in controls" :key="control.key" class="light-control"><span>{{ control.label }}<output>{{ values[control.key].toFixed(2) }}{{ control.unit }}</output></span><input type="range" :aria-label="control.label" :min="control.min" :max="control.max" :step="control.step" :value="values[control.key]" @input="adjust(control.key, $event)" /></label></fieldset>
        <div class="drawer-quality"><label>画质 <select v-model="quality" aria-label="画质"><option value="auto">自动</option><option value="high">高</option><option value="medium">中</option><option value="low">低 · 减少动态</option><option value="static">静态原画</option></select></label></div>
      </div></Transition>
    </section></Transition>
    <footer class="bottom-meta interface"><span>LIVING HERO <b>·</b> 02</span></footer>
    <div class="utility-bar" :class="{ 'immersive-only': immersive }">
      <div v-if="!immersive" class="view-picker"><span>画面</span><ThemedSelect :model-value="view" label="画面模式" :options="[{value:'lit',label:'实时光照'},{value:'base',label:'原始底图'},{value:'normal',label:'法线贴图'}]" @update:model-value="view = $event as RenderView" /></div>
      <span v-if="!immersive" class="utility-divider" />
      <button v-show="!immersive" ref="settingsButton" class="dock-toggle" :aria-expanded="menuOpen" aria-controls="scene-controls" @click="menuOpen = !menuOpen"><UiIcon name="settings" /><span>光影</span><UiIcon name="chevron" :class="{ rotated: menuOpen }" /></button>
      <span v-if="!immersive" class="utility-divider" />
      <button class="immersive-button" :aria-pressed="immersive" @click="immersive = !immersive"><UiIcon name="eye" />{{ immersive ? '显示界面' : '沉浸' }}</button>
    </div>
    <span class="page-notice" role="status">{{ notice }}</span>


  </main>
</template>
