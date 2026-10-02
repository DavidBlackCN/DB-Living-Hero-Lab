<script setup lang="ts">
defineProps<{ name: string }>()
const paths: Record<string, string> = {
 settings: 'M4 7h16M4 17h16M8 4v6M16 14v6',
 chevron: 'm7 14 5-5 5 5',
 moon: 'M20 14a8.5 8.5 0 0 1-10-10 8.5 8.5 0 1 0 10 10Z',
 sun: 'M12 3v2m0 14v2M3 12h2m14 0h2M5.6 5.6l1.4 1.4m10 10 1.4 1.4M5.6 18.4l1.4-1.4m10-10 1.4-1.4M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
 twilight: 'M3 17h18M5 21h14M6 14a6 6 0 0 1 12 0M12 2v3M3 7l2 2m14 0 2-2',
 play: 'm8 4 12 8-12 8Z', pause: 'M8 5v14M16 5v14',
 sparkle: 'm12 3 2.3 6.7L21 12l-6.7 2.3L12 21l-2.3-6.7L3 12l6.7-2.3Z',
 sync: 'M4 9a8 8 0 1 1 0 6M4 4v5h5',
 fullscreen: 'M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5',
 eye: 'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Zm13 0a3 3 0 1 1-6 0 3 3 0 0 1 6 0',
 mail: 'M3 5h18v14H3Zm0 1 9 7 9-7',
 bilibili: 'm7 3 3 3m7-3-3 3M4 7h16v13H4Zm4 5v3m8-3v3',
 github: 'M9 21v-4c-4 1-4-2-6-3m12 7v-4c0-1-.3-2-1-2 4-.5 6-2 6-5 0-1.5-.5-2.5-1.5-3.5.3-1 .2-2-.3-3-2 0-3 1-3 1a12 12 0 0 0-6.4 0s-1-1-3-1c-.5 1-.6 2-.3 3C4.5 7.5 4 8.5 4 10c0 3 2 4.5 6 5-.7 0-1 1-1 2',
 qq: 'M7 10V8a5 5 0 0 1 10 0v2l3 6-3-1c0 3-2 5-5 5s-5-2-5-5l-3 1Zm2 0h.1m5.8 0h.1M9 14q3 2 6 0M7 21l3-1m4 0 3 1',
}
</script>
<template><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="ui-icon" aria-hidden="true"><path :d="paths[name] ?? paths.sparkle" /></svg></template>
