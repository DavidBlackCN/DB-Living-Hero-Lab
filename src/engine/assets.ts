import { validateBlinkMetadata } from './animation';
export interface AssetOptions { baseUrl?: string; normalUrl?: string; maskUrl?: string; sceneMaskUrl?: string; lightShapingUrl?: string; correctionUrl?: string; blinkMetadataUrl?: string }
export async function loadImage(url: string) {
  const image = new Image(); image.src = url;
  try { await image.decode(); } catch { throw new Error(`无法加载素材：${url}`); }
  return image;
}
export async function loadAssets(options: AssetOptions) {
  const [base, normal, mask, sceneMask, lightShaping, correction] = await Promise.all([
    loadImage(options.baseUrl ?? '/assets/hero-4k-digital-art.png'),
    options.normalUrl ? loadImage(options.normalUrl) : undefined,
    options.maskUrl ? loadImage(options.maskUrl) : undefined,
    options.sceneMaskUrl ? loadImage(options.sceneMaskUrl) : undefined,
    options.lightShapingUrl ? loadImage(options.lightShapingUrl) : undefined,
    options.correctionUrl ? loadImage(options.correctionUrl) : undefined,
  ]);
  for (const map of [normal, mask, sceneMask, correction]) {
    if (map && (map.width !== base.width || map.height !== base.height)) throw new Error('辅助资产必须与原图尺寸一致');
  }
  if(lightShaping && lightShaping.width*base.height !== lightShaping.height*base.width) throw new Error('空间遮挡图必须与原图保持相同比例和配准');
  const blink = options.blinkMetadataUrl ? await loadBlink(options.blinkMetadataUrl, base.width, base.height) : undefined;
  return { base, normal, mask, sceneMask, lightShaping, correction, blink };
}

async function loadBlink(url: string, width: number, height: number) {
  const metadataUrl = new URL(url, document.baseURI);
  const response = await fetch(metadataUrl);
  if (!response.ok) throw new Error(`Cannot load Blink metadata: ${response.status}`);
  const metadata: unknown = await response.json();
  validateBlinkMetadata(metadata, width, height);
  const [half, closed] = await Promise.all([
    loadImage(new URL(metadata.states.half, metadataUrl).href),
    loadImage(new URL(metadata.states.closed, metadataUrl).href),
  ]);
  for (const image of [half, closed]) {
    if (image.width !== metadata.crop.width || image.height !== metadata.crop.height) {
      throw new Error('Blink overlay dimensions do not match registered crop');
    }
  }
  return { metadata, half, closed };
}
