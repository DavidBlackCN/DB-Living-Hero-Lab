/**
 * Contract for a future registered blink asset. The renderer deliberately does
 * not synthesize eye geometry: the overlay must come from an exact local crop
 * or a registered closed-eye frame made for the approved hero artwork.
 */
export interface BlinkAsset {
  url: string;
  width: number;
  height: number;
  registration: { x: number; y: number; width: number; height: number };
}

export interface BlinkOptions {
  asset?: BlinkAsset;
  enabled: boolean;
  durationMs: number;
  cooldownMs: number;
}

export const defaultBlinkOptions: BlinkOptions = {
  enabled: false,
  durationMs: 140,
  cooldownMs: 3200,
};

export function canUseBlinkAsset(asset: BlinkAsset | undefined, baseWidth: number, baseHeight: number) {
  return Boolean(
    asset &&
    asset.width === baseWidth &&
    asset.height === baseHeight &&
    asset.registration.width > 0 &&
    asset.registration.height > 0,
  );
}
