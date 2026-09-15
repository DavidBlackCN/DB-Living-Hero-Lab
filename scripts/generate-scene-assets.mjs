import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

// Vector data assets only. Never reads/writes/repaints the approved base illustration.
const regions = JSON.parse(await readFile(new URL('../docs/scene-regions.json', import.meta.url), 'utf8'));
const output = new URL('../public/assets/generated/', import.meta.url);
await mkdir(output, { recursive: true });
const path = (name, fill) => `<path d="${regions[name]}" fill="${fill}"/>`;
const header = `<svg xmlns="http://www.w3.org/2000/svg" width="3840" height="2160" viewBox="0 0 1200 675" color-interpolation="sRGB">`;
const feather = `<filter id="soft" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="1.15"/></filter>`;
const occluders = ['hair', 'cloth', 'face', 'hat', 'lamp', 'vase', 'pictureFrame', 'penCup'];

const masks = `${header}<defs>${feather}</defs><rect width="1200" height="675" fill="black"/>
<g filter="url(#soft)">${path('hair', '#00ff00')}${path('cloth', '#0000ff')}${path('bodice', '#0000ff')}${path('face', '#ff0000')}${path('handLeft', '#000000')}${path('handRight', '#000000')}</g></svg>`;

const scene = `${header}<defs>${feather}</defs><rect width="1200" height="675" fill="black"/>
<g filter="url(#soft)">${path('windowGlassLeft', '#ff0000')}${path('windowGlassRight', '#ff0000')}${occluders.map(n => path(n, '#000000')).join('')}
${path('desk', '#00ff00')}${['book', 'cup', 'books', 'handLeft', 'handRight'].map(n => path(n, '#000000')).join('')}
${path('lampEmitter', '#0000ff')}</g></svg>`;

// Low-frequency orientation fields, gated by the same contours as the material map.
// R/G encode image-space X/Y, B encodes Z toward viewer; shader renormalizes.
const normals = `${header}<defs>${feather}
<linearGradient id="hair" x1="0" x2="1"><stop stop-color="#6280f7"/><stop offset=".5" stop-color="#8080ff"/><stop offset="1" stop-color="#a080f7"/></linearGradient>
<radialGradient id="face" cx=".35" cy=".35" r=".8"><stop stop-color="#7c7aff"/><stop offset="1" stop-color="#8a88fd"/></radialGradient>
<linearGradient id="cloth"><stop stop-color="#7182fb"/><stop offset=".5" stop-color="#8080ff"/><stop offset="1" stop-color="#8b80fc"/></linearGradient>
</defs><rect width="1200" height="675" fill="#8080ff"/>
<g filter="url(#soft)">${path('desk', '#804bee')}${path('book', '#8076fe')}${path('cup', '#8080ff')}${path('books', '#8080ff')}
${path('hair', 'url(#hair)')}${path('cloth', 'url(#cloth)')}${path('bodice', 'url(#cloth)')}${path('face', 'url(#face)')}${path('handLeft', '#8080ff')}${path('handRight', '#8080ff')}</g></svg>`;

for (const [name, source] of Object.entries({ 'character-masks.svg': masks, 'scene-masks.svg': scene, 'normal-low-frequency.svg': normals })) {
  await writeFile(new URL(name, output), source + '\n');
  console.log(`Generated ${fileURLToPath(new URL(name, output))}`);
}
