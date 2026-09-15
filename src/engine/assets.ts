export interface AssetOptions { baseUrl?: string; normalUrl?: string; maskUrl?: string; sceneMaskUrl?: string }
export async function loadImage(url: string) {
  const image = new Image(); image.src = url;
  try { await image.decode(); } catch { throw new Error(`无法加载素材：${url}`); }
  return image;
}
export async function loadAssets(options: AssetOptions) {
  const [base, normal, mask, sceneMask] = await Promise.all([
    loadImage(options.baseUrl ?? '/assets/hero-4k-digital-art.png'),
    options.normalUrl ? loadImage(options.normalUrl) : undefined,
    options.maskUrl ? loadImage(options.maskUrl) : undefined,
    options.sceneMaskUrl ? loadImage(options.sceneMaskUrl) : undefined,
  ]);
  for (const map of [normal, mask, sceneMask]) {
    if (map && (map.width !== base.width || map.height !== base.height)) throw new Error('辅助资产必须与原图尺寸一致');
  }
  return { base, normal, mask, sceneMask };
}
