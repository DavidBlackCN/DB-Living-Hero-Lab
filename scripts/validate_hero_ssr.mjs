import { createServer } from 'vite'
import { createSSRApp } from 'vue'
import { renderToString } from 'vue/server-renderer'
const server = await createServer({ server: { middlewareMode: true } })
try {
  const { LivingHero } = await server.ssrLoadModule('/src/index.ts')
  const html = await renderToString(createSSRApp(LivingHero, { assetRoot: '/blog/assets/hero', minutes: 720 }))
  if (!html.includes('/blog/assets/hero/base/base-albedo.png') || html.includes('<canvas')) throw new Error('SSR poster contract failed')
  console.log('SSR passed: public entry, registered poster, no browser initialization.')
} finally { await server.close() }
