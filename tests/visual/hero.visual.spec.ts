import { test } from '@playwright/test';

const times = [
  ['dawn', 360], ['noon', 720], ['dusk', 1050], ['night', 1380],
] as const;
const views = ['normal', 'masks', 'scene', 'overlay'] as const;

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.locator('#status').waitFor({ state: 'visible' });
  await page.locator('#animation').uncheck();
  await page.locator('#steam').uncheck();
  await page.locator('#reduced').check();
});

test('coffee steam enabled state', async ({ page }) => {
  await page.locator('#animation').check();
  await page.locator('#steam').check();
  await page.waitForTimeout(120);
  await page.screenshot({ path: 'docs/screenshots/phase3/steam-enabled.png', fullPage: true });
});

for (const [name, minutes] of times) {
  test(`visual baseline: ${name}`, async ({ page }) => {
    await page.locator('#time').fill(String(minutes));
    await page.locator('#time').dispatchEvent('change');
    await page.waitForTimeout(100);
    await page.screenshot({ path: `docs/screenshots/phase3/${name}.png`, fullPage: true });
  });
}

for (const view of views) {
  test(`visual debug: ${view}`, async ({ page }) => {
    await page.locator('#view').selectOption(view);
    await page.waitForTimeout(100);
    await page.screenshot({ path: `docs/screenshots/phase3/${view}.png`, fullPage: true });
  });
}
