import { test, expect } from '@playwright/test';
import { visualRoot } from './review-output';

const times = [
  ['dawn', 360], ['noon', 720], ['dusk', 1050], ['night', 1380],
] as const;
const views = ['normal', 'masks', 'scene', 'overlay', 'neutral'] as const;

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.locator('#status').waitFor({ state: 'visible' });
  await page.locator('#animation').uncheck();
  await page.locator('#steam').uncheck();
  await page.locator('#reduced').check();
});

for (const [name, minutes] of [['dusk', 1050], ['night', 1380]] as const) {
  test(`bloom comparison: ${name}`, async ({ page }) => {
    await page.locator('#time').fill(String(minutes));
    await page.locator('#time').dispatchEvent('change');
    await page.locator('input[type="checkbox"]#bloom').uncheck();
    await page.screenshot({ path: `${visualRoot}/phase4/${name}-bloom-off.png`, fullPage: true });
    await page.locator('input[type="checkbox"]#bloom').check();
    await page.screenshot({ path: `${visualRoot}/phase4/${name}-bloom-on.png`, fullPage: true });
  });
}

for (const view of ['bright', 'bloom'] as const) {
  test(`bloom debug: ${view}`, async ({ page }) => {
    await page.locator('#view').selectOption(view);
    await page.screenshot({ path: `${visualRoot}/phase4/${view}.png`, fullPage: true });
  });
}

test('coffee steam enabled state', async ({ page }) => {
  await page.locator('#animation').check();
  await page.locator('#steam').check();
  await page.waitForTimeout(120);
  await page.screenshot({ path: `${visualRoot}/phase3/steam-enabled.png`, fullPage: true });
});

test('bloom controls preserve independent settings', async ({ page }) => {
  const state = await page.evaluate(() => (window as Window & { livingHero?: { setSettings: (settings: Record<string, number>) => void; getState: () => unknown } }).livingHero?.getState());
  if (!state) throw new Error('Living Hero engine did not initialize');
  await page.locator('#bloomIntensity').fill('0.14');
  await page.locator('#bloomThreshold').fill('0.91');
  await page.locator('#bloomRadius').fill('1.45');
  await page.locator('input[type="checkbox"]#bloom').uncheck();
  await page.locator('input[type="checkbox"]#bloom').check();
  const settings = await page.evaluate(() => (window as unknown as { livingHero: { getSettings: () => Record<string, number> } }).livingHero.getSettings());
  expect(settings.bloom).toBe(.14);
  expect(settings.bloomThreshold).toBe(.91);
  expect(settings.bloomRadius).toBe(1.45);
  await page.screenshot({ path: `${visualRoot}/phase4/bloom-controls.png`, fullPage: true });
});

test('runtime GPU stats expose quarter-resolution bloom targets', async ({ page }) => {
  const stats = await page.evaluate(() => (window as unknown as { livingHero: { getStats: () => Record<string, number | boolean> } }).livingHero.getStats());
  expect(stats.artworkWidth).toBe(3840);
  expect(stats.artworkHeight).toBe(2160);
  expect(stats.sourceTextureMiB).toBe(99.75);
  expect(stats.contextLost).toBe(false);
});

for (const dpr of [1, 1.5]) {
  test(`bloom DPR ${dpr}`, async ({ browser }) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: dpr, reducedMotion: 'reduce' });
    try {
      const page = await context.newPage();
      const errors: string[] = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto('http://127.0.0.1:4173');
      await page.locator('#animation').uncheck();
      await page.getByRole('button', { name: 'Dusk', exact: true }).click();
      await expect(page.locator('#clock')).toHaveText('17:30');
      const result = await page.locator('#hero').evaluate((element: HTMLCanvasElement) => {
        const gl = element.getContext('webgl2')!;
        return { width: element.width, height: element.height, error: gl.getError() };
      });
      expect(result).toEqual({ width: 1440*dpr, height: 900*dpr, error: 0 });
      expect(errors).toEqual([]);
      await page.screenshot({ path: `${visualRoot}/phase4/dusk-dpr-${dpr}.png` });
    } finally { await context.close(); }
  });
}

for (const [name, minutes] of times) {
  test(`visual baseline: ${name}`, async ({ page }) => {
    await page.locator('#time').fill(String(minutes));
    await page.locator('#time').dispatchEvent('change');
    await page.waitForTimeout(100);
    await page.screenshot({ path: `${visualRoot}/phase3/${name}.png`, fullPage: true });
  });
}

for (const view of views) {
  test(`visual debug: ${view}`, async ({ page }) => {
    await page.locator('#view').selectOption(view);
    await page.waitForTimeout(100);
    await page.screenshot({ path: `${visualRoot}/phase3/${view}.png`, fullPage: true });
  });
}

test('directional structure snapshots across key times', async ({ page }) => {
  for (const [name, minutes] of [['morning', 480], ['noon', 720], ['dusk', 1050], ['night', 1380]] as const) {
    await page.locator('#time').fill(String(minutes));
    await page.locator('#time').dispatchEvent('change');
    await page.waitForTimeout(100);
    await page.screenshot({ path: `${visualRoot}/phase-next/${name}-final.png`, fullPage: true });
    await page.locator('#view').selectOption('neutral');
    await page.screenshot({ path: `${visualRoot}/phase-next/${name}-neutral.png`, fullPage: true });
    await page.locator('#view').selectOption('final');
  }
});

test('projected window light keyframes and night window boundary', async ({ page }) => {
  for (const [name, minutes] of [['morning', 480], ['noon', 720], ['dusk', 1050]] as const) {
    await page.locator('#time').fill(String(minutes));
    await page.locator('#time').dispatchEvent('change');
    await page.waitForTimeout(100);
    await page.screenshot({ path: `${visualRoot}/projected/${name}-final.png`, fullPage: true });
    await page.locator('#view').selectOption('neutral');
    await page.screenshot({ path: `${visualRoot}/projected/${name}-neutral.png`, fullPage: true });
    await page.locator('#view').selectOption('projected');
    await page.screenshot({ path: `${visualRoot}/projected/${name}-projected.png`, fullPage: true });
    await page.locator('#view').selectOption('final');
  }
  await page.locator('#time').fill('1380');
  await page.locator('#time').dispatchEvent('change');
  await page.locator('#view').selectOption('scene');
  await page.screenshot({ path: `${visualRoot}/projected/night-scene.png`, fullPage: true });
  await page.locator('#view').selectOption('overlay');
  await page.screenshot({ path: `${visualRoot}/projected/night-overlay.png`, fullPage: true });
  await page.locator('#view').selectOption('final');
  await page.screenshot({ path: `${visualRoot}/projected/night-final.png`, fullPage: true });
});
