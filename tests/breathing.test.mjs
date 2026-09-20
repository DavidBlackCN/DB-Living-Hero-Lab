import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {test} from 'node:test';
import ts from 'typescript';
const source=await readFile(new URL('../src/engine/breathing.ts',import.meta.url),'utf8');
const js=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
const {BreathingClock}=await import(`data:text/javascript;base64,${Buffer.from(js).toString('base64')}`);
test('breathing cosine starts neutral, peaks at half-cycle and returns smoothly',()=>{
  const c=new BreathingClock();c.update(0,5.4);
  assert.equal(c.amount,0);c.update(1350,5.4);assert.ok(Math.abs(c.amount-.5)<1e-10);
  c.update(2700,5.4);assert.equal(c.amount,1);c.update(5400,5.4);assert.equal(c.amount,0);
});
test('hidden time is excluded and reset is neutral',()=>{
  const c=new BreathingClock();c.update(0,5.4);c.update(1000,5.4);
  const phase=c.phase;c.pause();c.update(100000,5.4);assert.equal(c.phase,phase);
  c.update(101000,5.4);assert.ok(c.phase>phase);c.reset();assert.equal(c.amount,0);
  c.update(200000,5);assert.equal(c.phase,0);
});
test('cycle changes and repeated timestamps stay finite and bounded',()=>{
  const c=new BreathingClock();
  for(let i=0;i<1000;i++){c.update(i*33,i%2?5:6);assert.ok(c.amount>=0&&c.amount<=1);}
  const phase=c.phase;c.update(999*33,6);assert.equal(c.phase,phase);
});
