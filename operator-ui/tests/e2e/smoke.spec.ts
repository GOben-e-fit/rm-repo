import { expect, test } from '@playwright/test';

test('overview page renders', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Plattform-Übersicht')).toBeVisible();
});

test('health endpoint returns ok', async ({ request }) => {
  const res = await request.get('/api/health');
  expect(res.status()).toBe(200);
  const body = await res.json();
  expect(body.status).toBe('ok');
  expect(body.service).toBe('rm-ki-operator-ui');
});
