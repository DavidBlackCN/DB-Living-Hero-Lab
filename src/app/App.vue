<script setup lang="ts">
import { computed, ref } from 'vue'
import LivingHero from '../components/LivingHero.vue'
import type { LivingHeroHandle, TimeSnapshot } from '../index'
import { homepage } from './homepage'
import './homepage.css'
const hero = ref<LivingHeroHandle | null>(null)
const sceneTime = ref<TimeSnapshot>({ mode: 'realtime', minutes: 720 })
const presets = [{ name: '晨曦', minutes: 390 }, { name: '白昼', minutes: 720 }, { name: '薄暮', minutes: 1050 }, { name: '夜色', minutes: 1320 }]
const clock = computed(() => `${String(Math.floor(sceneTime.value.minutes / 60) % 24).padStart(2, '0')}:${String(Math.floor(sceneTime.value.minutes % 60)).padStart(2, '0')}`)
const period = computed(() => { const m = sceneTime.value.minutes; return m < 300 || m >= 1140 ? '夜色' : m < 480 ? '晨曦' : m < 990 ? '白昼' : '薄暮' })
</script>

<template>
  <main class="sample-home" id="top">
    <a class="skip-link" href="#explore">跳到首页内容</a>
    <div class="homepage-scene">
    <LivingHero ref="hero" class="homepage-hero" debug entrance @time-change="sceneTime = $event">
      <template #loading="{ loaded, total }"><div class="arrival-status" role="status"><span>光影正在醒来</span><progress :value="loaded" :max="total" aria-label="场景加载进度" /></div></template>
      <template #fallback="{ reason, retry }"><div v-if="reason" class="arrival-status" role="status">已显示静态原画 <button @click="retry">重试动态场景</button></div></template>
    </LivingHero>
      <div class="home-interface">
        <header class="home-header">
          <a class="home-brand" href="#top"><span class="brand-monogram">DB<span>·</span></span><span>{{ homepage.name }}<small>NOTES & LITTLE WONDERS</small></span></a>
          <nav aria-label="主导航"><a href="#explore">记录</a><a href="#about">关于</a><a :href="homepage.github" target="_blank" rel="noopener noreferrer">GitHub ↗</a></nav>
        </header>
        <section class="home-intro" aria-labelledby="home-title">
          <p class="home-eyebrow"><span /> A QUIET CORNER OF THE INTERNET</p>
          <h1 id="home-title">在光影之间，<br />留一页<span>给生活。</span></h1>
          <p class="home-description">{{ homepage.description }}</p>
          <div class="home-actions"><a class="home-primary" href="#explore">随便逛逛 <span>↓</span></a><a class="home-secondary" href="#about">关于这个角落 <span>↗</span></a></div>
        </section>
        <footer class="home-scene-footer">
          <div class="scene-note"><span class="live-dot" />{{ sceneTime.mode === 'realtime' ? '与此刻同频' : '时光预览' }}<span class="scene-note-rule" />{{ period }} <time>{{ clock }}</time></div>
          <div class="scene-presets" aria-label="场景时段"><button v-for="preset in presets" :key="preset.name" :aria-pressed="Math.abs(sceneTime.minutes - preset.minutes) < 1" @click="hero?.setTime(preset.minutes)">{{ preset.name }}</button><button class="sync-scene" :disabled="sceneTime.mode === 'realtime'" @click="hero?.backToNow()">此刻 ↺</button></div>
          <a class="scroll-cue" href="#explore">往下看看 <span>↓</span></a>
        </footer>
      </div>
    </div>
    <section id="explore" class="home-explore" aria-labelledby="explore-title">
      <div class="section-heading"><div><p class="section-kicker">01 / FIELD NOTES</p><h2 id="explore-title">一些记录，一点探索。</h2></div><p>从一张插画，到一个会呼吸的角落。</p></div>
      <div class="home-records"><a v-for="(entry, index) in homepage.entries" :key="entry.title" class="home-record" :href="entry.url" target="_blank" rel="noopener noreferrer"><span class="record-number">0{{ index + 1 }}</span><div><p class="record-category">{{ entry.category }}</p><h3>{{ entry.title }}</h3><p>{{ entry.description }}</p></div><span class="record-arrow">↗</span></a></div>
    </section>
    <section id="about" class="home-about" aria-labelledby="about-title"><p class="section-kicker">02 / ABOUT THIS CORNER</p><div><h2 id="about-title">你好，我是 {{ homepage.name }}。</h2><p>这里是个人主页的一个小小预演。写下探索，也收藏日常；让技术留在幕后，让光影陪伴阅读。</p><p class="about-caption">Black Sister · Living Hero / 以真实本地时间，慢慢走过一天。</p></div><a :href="homepage.github" target="_blank" rel="noopener noreferrer">在 GitHub 相遇 ↗</a></section>
    <footer class="home-colophon"><span>DAVIDBLACKCN / LIVING HERO</span><span>示例主页 · 慢一点，也很好。</span><a href="#top">回到顶部 ↑</a></footer>
  </main>
</template>
