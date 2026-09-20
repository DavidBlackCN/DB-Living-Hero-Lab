import { readFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
import { test } from 'node:test';
import ts from 'typescript';

const source = await readFile(new URL('../src/engine/animation.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } }).outputText;
const { BlinkController, validateBlinkMetadata } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`);
const metadata = JSON.parse(await readFile(new URL('../public/assets/generated/blink/blink-metadata.json', import.meta.url), 'utf8'));

test('single blink follows open / half / closed / half / open in 160 ms', () => {
  const b = new BlinkController(() => 0);
  assert.equal(b.phase, 'open');
  assert.equal(b.trigger(0), true);
  assert.equal(b.trigger(1), false);
  for (const [time, phase] of [[0,'half'],[39,'half'],[40,'closed'],[109,'closed'],[110,'half'],[159,'half'],[160,'open']]) {
    b.update(time); assert.equal(b.phase, phase);
  }
  assert.equal(b.delay, 2800);
});
test('automatic intervals span 2.8-5.5 seconds without idle RAF', () => {
  for (const random of [0, .5, 1]) {
    const b = new BlinkController(() => random);
    assert.equal(b.delay, 2800 + 2700 * random);
    b.update(0); b.update(b.delay - 1); assert.equal(b.phase, 'open');
    b.update(2800 + 2700 * random); assert.equal(b.phase, 'half');
    b.update(30000); assert.equal(b.phase, 'open');
    assert.equal(b.delay, 2800 + 2700 * random);
  }
});
test('pause excludes background time, reset immediately returns to open', () => {
  const b = new BlinkController(() => 0);
  b.update(0); b.update(1000); b.pause(); b.update(60000);
  assert.equal(b.delay, 1800);
  b.trigger(60000); b.update(60050); b.pause(); b.update(120000);
  assert.equal(b.phase, 'closed');
  b.update(120060); assert.equal(b.phase, 'half');
  b.reset(); assert.equal(b.phase, 'open'); assert.equal(b.delay, 2800);
  b.update(200000); assert.equal(b.phase, 'open');
});
test('metadata validates local crop, canvas, alpha, states and finite bounds', () => {
  assert.doesNotThrow(() => validateBlinkMetadata(metadata,3840,2160));
  for (const invalid of [null, {}, {...metadata,alpha:'premultiplied'}, {...metadata,states:{half:''}},
    {...metadata,crop:{...metadata.crop,x:-1}}, {...metadata,crop:{...metadata.crop,width:0}},
    {...metadata,crop:{...metadata.crop,y:Infinity}}, {...metadata,crop:{...metadata.crop,x:3800}}]) {
    assert.throws(() => validateBlinkMetadata(invalid,3840,2160));
  }
  assert.throws(() => validateBlinkMetadata(metadata,1920,1080));
});
