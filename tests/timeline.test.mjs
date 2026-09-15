import { readFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
import { test } from 'node:test';
import ts from 'typescript';

// Test the actual TypeScript sources without emitting build files or adding a test framework.
const compile = source => ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } }).outputText;
const url = source => `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
const timelineUrl = url(compile(await readFile(new URL('../src/engine/timeline.ts', import.meta.url), 'utf8')));
const { Timeline, wrapTime, formatTime, localMinutes } = await import(timelineUrl);
const lightingSource = compile(await readFile(new URL('../src/engine/lighting.ts', import.meta.url), 'utf8')).replace("'./timeline'", JSON.stringify(timelineUrl));
const { lightingAt } = await import(url(lightingSource));

test('24h endpoint and negative times wrap consistently', () => {
  assert.equal(wrapTime(1440), 0); assert.equal(wrapTime(-1), 1439);
  assert.equal(formatTime(1440), '00:00'); assert.equal(formatTime(1050), '17:30');
});
test('midnight transition takes the short path and converges', () => {
  const t = new Timeline(1430); t.setTime(10); t.update(1/60,false);
  assert.ok(t.minutes > 1430 || t.minutes < 10);
  for(let i=0;i<200;i++) t.update(1/60,false);
  assert.equal(t.minutes,10);
});
test('manual scrubbing disables realtime; reduced motion snaps to requested time', () => {
  const t=new Timeline(); t.realtime=true; t.setTime(360); t.update(1/60,true);
  assert.equal(t.realtime,false); assert.equal(t.minutes,360);
  assert.throws(()=>t.setTime(NaN));
});
test('realtime uses local wall clock', () => {
  const t=new Timeline(); t.realtime=true; t.update(.016,true);
  const difference=Math.abs(t.minutes-localMinutes()); assert.ok(difference<.1 || difference>1439.9);
});
test('lighting is finite across the full day and continuous at midnight and keyframes', () => {
  for(let m=0;m<=1440;m++) {
    const l=lightingAt(m); assert.ok([...l.ambient,...l.sun,...l.direction,l.lamp,l.night].every(Number.isFinite));
    assert.ok(l.night >= 0 && l.night <= 1);
  }
  for(const m of [0,300,360,540,720,930,1050,1140,1380,1440]) {
    const a=lightingAt(m-.001),b=lightingAt(m+.001);
    assert.ok(a.ambient.every((v,i)=>Math.abs(v-b.ambient[i])<.001));
    assert.ok(Math.abs(a.lamp-b.lamp)<.001);
    assert.ok(Math.abs(a.night-b.night)<.001);
  }
});
test('night suppression is off at noon and strongest at night', () => {
  assert.equal(lightingAt(720).night, 0);
  assert.equal(lightingAt(1380).night, 1);
  assert.ok(lightingAt(360).night < lightingAt(1050).night);
});
