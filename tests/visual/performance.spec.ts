import { test, expect } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import { performanceRoot } from './review-output';

type Sample = {
  dpr: number;
  bloom: boolean;
  canvas: { width: number; height: number };
  estimatedCanvasMiB: number;
  estimatedSourceTexturesMiB: number;
  estimatedBloomMiB: number;
  medianFrameMs: number;
  p95FrameMs: number;
  webglError: number;
  pageErrors: string[];
};

async function measure(page: import('@playwright/test').Page, dpr: number, bloom: boolean): Promise<Sample> {
  await page.goto('/');
  await page.locator('#status').waitFor({ state: 'visible' });
  await page.locator('#animation').check();
  await page.locator('#steam').check();
  await page.locator('input[type="checkbox"]#bloom').setChecked(bloom);
  await page.getByRole('button', { name: 'Dusk', exact: true }).click();
  const pageErrors: string[] = [];
  const listener = (error: Error) => pageErrors.push(error.message);
  page.on('pageerror', listener);
  const result = await page.evaluate(async () => {
    const canvas = document.querySelector<HTMLCanvasElement>('#hero')!;
    const frames = await new Promise<number[]>(resolve => {
      const values: number[] = [];
      let previous = 0;
      const tick = (now: number) => {
        if (previous) values.push(now - previous);
        previous = now;
        if (values.length < 45) requestAnimationFrame(tick);
        else resolve(values);
      };
      requestAnimationFrame(tick);
    });
    const sorted = frames.slice().sort((a, b) => a - b);
    const percentile = (p: number) => sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * p))];
    const gl = canvas.getContext('webgl2')!;
    return {
      width: canvas.width,
      height: canvas.height,
      median: percentile(.5),
      p95: percentile(.95),
      webglError: gl.getError(),
      sourceTextureMiB: window.livingHero.getStats().sourceTextureMiB,
    };
  });
  page.off('pageerror', listener);
  const pixels = result.width * result.height;
  return {
    dpr, bloom, canvas: { width: result.width, height: result.height },
    estimatedCanvasMiB: Number((pixels * 4 / 1048576).toFixed(2)),
    estimatedSourceTexturesMiB: result.sourceTextureMiB,
    estimatedBloomMiB: Number((Math.ceil(result.width / 4) * Math.ceil(result.height / 4) * 4 * 3 / 1048576).toFixed(2)),
    medianFrameMs: Number(result.median.toFixed(2)),
    p95FrameMs: Number(result.p95.toFixed(2)),
    webglError: result.webglError,
    pageErrors,
  };
}

for (const dpr of [1, 1.5]) {
  test(`bloom performance DPR ${dpr}`, async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: dpr, reducedMotion: 'no-preference' });
    try {
      const page = await context.newPage();
      const samples = [await measure(page, dpr, false), await measure(page, dpr, true)];
      for (const sample of samples) {
        expect(sample.webglError).toBe(0);
        expect(sample.pageErrors).toEqual([]);
        expect(sample.canvas).toEqual({ width: 1440 * dpr, height: 900 * dpr });
      }
      await mkdir(performanceRoot, { recursive: true });
      await writeFile(`${performanceRoot}/bloom-dpr-${dpr}.json`, JSON.stringify(samples, null, 2) + '\n');
    } finally { await context.close(); }
  });
}
