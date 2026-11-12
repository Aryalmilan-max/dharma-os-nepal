const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const A=require('../web/assessment-core.js');
const modules=JSON.parse(fs.readFileSync(path.join(__dirname,'../skills/dharma-os/references/nepal-tech-intelligence/organization-needs.json'))).modules;
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'../examples/assessment-review/synthetic-shop.json')));
const today='2026-11-12';
const noContext=structuredClone(original);delete noContext.context;assert.equal(A.validate(noContext,modules,today).valid,false);
noContext.requirements.find(m=>m.id==='backup').assessment='NOT_ASSESSED';assert.equal(A.validate(noContext,modules,today).valid,true);
const summary=A.summary(original,modules,today);
assert.equal(summary.counts.GAP,1);assert.equal(summary.counts.NOT_ASSESSED,7);
assert.equal(summary.actions[0].id,'backup');assert.equal(summary.actions[0].priority,'IMMEDIATE_REVIEW');
assert.ok(A.markdown(original,modules,today).includes('SYNTHETIC DEMONSTRATION'));
assert.ok(A.markdown(original,modules,today).includes('NOT_ASSESSED: 7'));
for(const change of [m=>m.evidence=[],m=>m.assessment='MET',m=>m.assessment='NOT_APPLICABLE',m=>m.evidence=null,m=>m.acceptance=[],m=>m.evidence[0].checked_on='2026-02-30',m=>m.evidence[0].url='javascript:alert(1)',m=>m.impact=true]){
 const p=structuredClone(original);change(p.requirements.find(m=>m.id==='backup'));assert.equal(A.validate(p,modules,today).valid,false);
 assert.throws(()=>A.markdown(p,modules,today));
}
const met=structuredClone(original),m=met.requirements.find(m=>m.id==='backup');
Object.assign(m,{assessment:'MET',reviewer:'Synthetic reviewer',reviewed_on:today,acceptance_evidence:'SYNTHETIC-RETEST-02'});
assert.equal(A.validate(met,modules,today).valid,true);
assert.ok(A.markdown(met,modules,today).includes('SYNTHETIC-RETEST-02'));
const escaped=structuredClone(original);escaped.requirements[0].title='<script>unsafe()</script>';
const printable=A.html(escaped,modules,today);assert.ok(!printable.includes('<script>'));assert.ok(printable.includes('&lt;script&gt;'));
assert.ok(printable.includes('NOT_ASSESSED: 7'));assert.ok(printable.includes('SYNTHETIC DEMONSTRATION'));
for(const bad of [null,[],{}, {requirements:[null]}])assert.equal(A.validate(bad,modules,today).valid,false);
console.log('Assessment core: unknowns, action order, observed evidence, acceptance/reviewer gates, malformed input and bounded report passed.');
