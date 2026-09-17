import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

// Technical data only. The flower extractor reads source colors; neither script
// writes/repaints the approved base illustration.
const regions = JSON.parse(await readFile(new URL('../docs/scene-regions.json', import.meta.url), 'utf8'));
const glass = JSON.parse(await readFile(new URL('../docs/window-glass.json', import.meta.url), 'utf8'));
const glassPolygon = (pane, fill) => `<polygon points="${glass[pane].map(p=>p.join(',')).join(' ')}" fill="${fill}"/>`;
const output = new URL('../public/assets/generated/', import.meta.url);
await mkdir(output, { recursive: true });
const path = (name, fill) => `<path d="${regions[name]}" fill="${fill}"/>`;
const header = `<svg xmlns="http://www.w3.org/2000/svg" width="3840" height="2160" viewBox="0 0 1200 675" color-interpolation="sRGB">`;
const feather = `<filter id="soft" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="1.15"/></filter>`;
const occluders = ['hair', 'cloth', 'face', 'hat', 'lamp', 'vase', 'pictureFrame'];
execFileSync('python', [fileURLToPath(new URL('./generate-flower-occlusion.py', import.meta.url))]);
const flowerData = (await readFile(new URL('window-flower-occlusion.png', output))).toString('base64');

const masks = `${header}<defs>${feather}</defs><rect width="1200" height="675" fill="black"/>
<g filter="url(#soft)">${path('hair', '#00ff00')}${path('cloth', '#0000ff')}${path('bodice', '#0000ff')}${path('face', '#ff0000')}${path('handLeft', '#000000')}${path('handRight', '#000000')}</g></svg>`;

// Right glass retains native edge coverage. Only the source's defocused left
// lower edge gets an inward alpha transition, clipped by the glass geometry.
const lowerTransition = glass.leftLowerTransition;
const scene = `${header}<defs>${feather}
<mask id="receivers"><rect width="1200" height="675" fill="black"/><g filter="url(#soft)">${path('chair','#666666')}${['lampSill','desk','book','cup','books'].map(n=>path(n,'white')).join('')}${path('penCup','#bbbbbb')}${path('penHolderReceiver','#bbbbbb')}${path('pictureFrame','#777777')}${path('vase','#777777')}${['hair','cloth','bodice'].map(n=>path(n,'black')).join('')}${['handLeft','handRight'].map(n=>path(n,'white')).join('')}${path('laptop','black')}</g></mask>
<linearGradient id="leftLower" gradientUnits="userSpaceOnUse" x1="${lowerTransition.inner[0]}" y1="${lowerTransition.inner[1]}" x2="${lowerTransition.edge[0]}" y2="${lowerTransition.edge[1]}"><stop stop-color="white"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>
<filter id="penEdge" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation=".8"/></filter>
<filter id="defocusedStem" x="-50%" y="-20%" width="200%" height="140%"><feGaussianBlur stdDeviation="2.5"/></filter>
<clipPath id="glassBounds">${glassPolygon('left', 'white')}${glassPolygon('right', 'white')}</clipPath>
<mask id="glass" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="675" style="mask-type:alpha">
${glassPolygon('left', 'url(#leftLower)')}${glassPolygon('right', 'white')}
</mask><mask id="flowerOcclusion" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="675"><image width="1200" height="675" href="data:image/png;base64,${flowerData}"/></mask></defs><rect width="1200" height="675" fill="black"/>
<g clip-path="url(#glassBounds)" mask="url(#glass)"><rect width="1200" height="675" fill="red"/>${occluders.map(n => path(n, '#000000')).join('')}<g filter="url(#penEdge)">${path('penCup', 'black')}</g><g filter="url(#defocusedStem)">${path('windowSoftForeground', 'black')}</g><rect width="1200" height="675" fill="black" mask="url(#flowerOcclusion)"/></g>
<rect width="1200" height="675" fill="#00ff00" mask="url(#receivers)" style="mix-blend-mode:screen"/>
<g filter="url(#soft)">${path('lampEmitter', '#0000ff')}</g></svg>`;

// Low-frequency orientation fields, gated by the same contours as the material map.
// R/G encode image-space X/Y, B encodes Z toward viewer; shader renormalizes.
const normals = `${header}<defs>${feather}
<linearGradient id="hair" x1="0" x2="1"><stop stop-color="#6280f7"/><stop offset=".5" stop-color="#8080ff"/><stop offset="1" stop-color="#a080f7"/></linearGradient>
<radialGradient id="face" cx=".35" cy=".35" r=".8"><stop stop-color="#7c7aff"/><stop offset="1" stop-color="#8a88fd"/></radialGradient>
<linearGradient id="cloth"><stop stop-color="#7182fb"/><stop offset=".5" stop-color="#8080ff"/><stop offset="1" stop-color="#8b80fc"/></linearGradient>
</defs><rect width="1200" height="675" fill="#8080ff"/>
<g filter="url(#soft)">${path('desk', '#804bee')}${path('book', '#8076fe')}${path('cup', '#8080ff')}${path('books', '#8080ff')}
${path('hair', 'url(#hair)')}${path('cloth', 'url(#cloth)')}${path('bodice', 'url(#cloth)')}${path('face', 'url(#face)')}${path('handLeft', '#8080ff')}${path('handRight', '#8080ff')}</g></svg>`;

// R window access, G room receiving weights, B contact occlusion. Reuse the
// formerly unused desktop G channel; no additional texture or depth field.
const access=regions.windowAccess;
const room=regions.roomParticipation;
const roomPaths=room.surfaces.map(s=>`<path d="${s.path}" fill="rgb(0,${Math.round(s.weight*255)},0)"/>`).join('');
const contactClips=[...new Set(regions.contactDetails.map(c=>c.receiver))].map(n=>`<clipPath id="contact-${n}">${path(n,'white')}</clipPath>`).join('');
// Tight attachment plus a faint, wider loss of ambient visibility. Both are
// clipped to the receiving object, never projected by shifting its silhouette.
const penumbra=regions.contactPenumbra;
const contactPenumbrae=regions.contactDetails.map(c=>`<g clip-path="url(#contact-${c.receiver})"><path d="${c.path}" fill="none" stroke="rgb(0,0,${Math.round(c.weight*penumbra.weight*255)})" stroke-width="${c.width*penumbra.widthScale}" stroke-linecap="round" filter="url(#contactPenumbra)"/></g>`).join('');
const contactPaths=regions.contactDetails.map(c=>`<g clip-path="url(#contact-${c.receiver})"><path d="${c.path}" fill="none" stroke="rgb(0,0,${Math.round(c.weight*255)})" stroke-width="${c.width}" stroke-linecap="round" filter="url(#contactDetail-${c.name})"/></g>`).join('');
const shaping=`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675" color-interpolation="sRGB">
<defs>${contactClips}<filter id="contactPenumbra" filterUnits="userSpaceOnUse" x="0" y="0" width="1200" height="675"><feGaussianBlur stdDeviation="${penumbra.feather}"/></filter>${regions.contactDetails.map(c=>`<filter id="contactDetail-${c.name}" filterUnits="userSpaceOnUse" x="0" y="0" width="1200" height="675"><feGaussianBlur stdDeviation="${c.feather}"/></filter>`).join('')}</defs>
<defs><mask id="desktop"><rect width="1200" height="675" fill="black"/>${path('desk','white')}${['hair','cloth','bodice','handLeft','handRight','book','cup','books','laptop'].map(n=>path(n,'black')).join('')}</mask><mask id="room"><rect width="1200" height="675" fill="white"/>${['hair','cloth','bodice','face','hat','handLeft','handRight','desk','book','cup','books','laptop'].map(n=>path(n,'black')).join('')}</mask><filter id="roomSoft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="${room.feather}"/></filter><linearGradient id="access" gradientUnits="userSpaceOnUse" x1="${access.fromX}" x2="${access.toX}"><stop stop-color="rgb(${access.minimum*255},0,0)"/><stop offset="1" stop-color="rgb(${access.maximum*255},0,0)"/></linearGradient><filter id="contact"><feGaussianBlur stdDeviation="2.2"/></filter></defs>
<g style="isolation:isolate"><rect width="1200" height="675" fill="url(#access)"/>
<g style="mix-blend-mode:screen" mask="url(#room)"><g filter="url(#roomSoft)">${roomPaths}</g></g>
<g style="mix-blend-mode:screen" mask="url(#desktop)" filter="url(#contact)">${path('bookContact','#0000cc')}${path('cupContact','#0000ff')}</g><g style="mix-blend-mode:screen">${contactPenumbrae}</g><g style="mix-blend-mode:screen">${contactPaths}</g></g></svg>`;

for (const [name, source] of Object.entries({ 'character-masks.svg': masks, 'scene-masks.svg': scene, 'normal-low-frequency.svg': normals, 'light-shaping.svg': shaping })) {
  await writeFile(new URL(name, output), source + '\n');
  console.log(`Generated ${fileURLToPath(new URL(name, output))}`);
}
