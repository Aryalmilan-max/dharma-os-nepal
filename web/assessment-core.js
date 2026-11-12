/* Offline assessment decisions. Exported for browser and Node verification. */
(function(root) {
  'use strict';
  const states=['NOT_ASSESSED','GAP','PARTIAL','MET','NOT_APPLICABLE'];
  const nonempty=v=>typeof v==='string'&&!!v.trim();
  function dateOK(v,today) {
    if(typeof v!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(v)) return false;
    const d=new Date(v+'T00:00:00Z');return Number.isFinite(+d)&&d.toISOString().slice(0,10)===v&&v<=today;
  }
  function validate(plan,modules,today=new Date().toISOString().slice(0,10)) {
    const errors=[],warnings=[];
    if(!plan||typeof plan!=='object'||Array.isArray(plan)) return {valid:false,errors:['Assessment must be an object'],warnings};
    for(const k of ['scale','organization_type']) if(!nonempty(plan[k])) errors.push(k+': text required');
    if(plan.country!=='Nepal') errors.push('country must be Nepal');
    if('is_synthetic' in plan&&typeof plan.is_synthetic!=='boolean')errors.push('is_synthetic must be a boolean');
    if(!Array.isArray(plan.requirements)||!plan.requirements.length||plan.requirements.length>100) return {valid:false,errors:[...errors,'requirements: 1–100 records required'],warnings};
    const ids=[];
    plan.requirements.forEach((m,i)=>{
      const p='requirements['+i+']';
      if(!m||typeof m!=='object'||Array.isArray(m)){errors.push(p+': object required');return;}
      if(typeof m.id!=='string'||!modules.some(x=>x.id===m.id)) errors.push(p+': known requirement ID required');
      ids.push(m.id);
      if(!nonempty(m.title)) errors.push(p+': title required');
      for(const field of ['requirement','evidence_to_collect','deliverable','acceptance','owner','next_action','rationale','target_date','reviewer','reviewed_on','acceptance_evidence'])if(field in m&&typeof m[field]!=='string')errors.push(p+': '+field+' must be text');
      if(!states.includes(m.assessment)) errors.push(p+': invalid assessment state');
      let es=m.evidence===undefined?[]:m.evidence;
      if(!Array.isArray(es)||es.length>100){errors.push(p+': evidence must be a list of at most 100 records');es=[];}
      es.forEach((e,j)=>{
        const ep=p+'.evidence['+j+']';
        if(!e||typeof e!=='object'||Array.isArray(e)){errors.push(ep+': object required');return;}
        for(const f of ['reference','locator','finding']) if(!nonempty(e[f])) errors.push(ep+': '+f+' required');
        if(!dateOK(e.checked_on,today)) errors.push(ep+': valid non-future AD checked_on required');
        else if((new Date(today)-new Date(e.checked_on))/86400000>90)warnings.push(ep+': evidence check older than 90 days; assess freshness for this use');
        if(e.url){try{const u=new URL(e.url);if(!['http:','https:'].includes(u.protocol)||!u.hostname||u.username||u.password)throw Error();}catch{errors.push(ep+': only HTTP(S) source URLs without credentials are allowed');}}
      });
      if(['GAP','PARTIAL','MET'].includes(m.assessment)&&!es.length) errors.push(p+': observed assessment needs evidence; otherwise retain NOT_ASSESSED');
      if(m.assessment!=='NOT_ASSESSED'&&!nonempty(m.rationale)) errors.push(p+': assessment rationale required');
      if(['MET','NOT_APPLICABLE'].includes(m.assessment)&&(!nonempty(m.reviewer)||!dateOK(m.reviewed_on,today))) errors.push(p+': reviewer role and valid review date required');
      if(m.assessment==='MET'&&!nonempty(m.acceptance_evidence)) errors.push(p+': MET needs an actual acceptance evidence reference');
      if(m.assessment==='NOT_ASSESSED')warnings.push(p+': unknown; investigate before making a purchase/readiness claim');
      if(['GAP','PARTIAL'].includes(m.assessment)){
        for(const f of ['owner','next_action'])if(!nonempty(m[f])||m[f]==='TO_BE_ASSIGNED')warnings.push(p+': assign '+f);
        if(!m.target_date)warnings.push(p+': agree an action target date');
      }
      for(const f of ['impact','urgency'])if(m[f]!=null&&(!Number.isInteger(m[f])||m[f]<1||m[f]>5))errors.push(p+': '+f+' must be an integer from 1 to 5 or null');
      if(m.target_date&&!dateOK(m.target_date,'9999-12-31'))errors.push(p+': target_date must be AD YYYY-MM-DD');
      if(es.length&&m.assessment==='NOT_ASSESSED')warnings.push(p+': evidence recorded but assessment remains unresolved');
    });
    if(new Set(ids).size!==ids.length)errors.push('Duplicate requirement IDs');
    if(plan.is_synthetic)warnings.unshift('SYNTHETIC DEMONSTRATION — not real institutional or customer evidence');
    warnings.push('Only included requirements are reviewed; omitted requirements and sector obligations are not established as covered.');
    return {valid:!errors.length,errors,warnings,meaning:'Structural review only. Source truth, authority, applicability and acceptance adequacy need human review.'};
  }
  function summary(plan,modules,today) {
    const review=validate(plan,modules,today);if(!review.valid)throw Error(review.errors.join('; '));
    const counts={},actions=[];
    for(const m of plan.requirements){counts[m.assessment]=(counts[m.assessment]||0)+1;
      if(!['NOT_ASSESSED','GAP','PARTIAL'].includes(m.assessment))continue;
      const score=(m.impact||0)*(m.urgency||0);
      actions.push({id:m.id,title:m.title,state:m.assessment,action:m.next_action||'Collect current-state evidence',owner:m.owner||'TO_BE_ASSIGNED',target_date:m.target_date||'NOT_AGREED',priority:m.assessment==='NOT_ASSESSED'?'INVESTIGATE':!score?'UNRANKED':score>=16?'IMMEDIATE_REVIEW':score>=9?'HIGH':'PLANNED',heuristic_score:score});
    }
    actions.sort((a,b)=>(Number(a.state==='NOT_ASSESSED')-Number(b.state==='NOT_ASSESSED'))||b.heuristic_score-a.heuristic_score||a.id.localeCompare(b.id));
    return {status:'HUMAN_DECISION_REQUIRED',counts,actions,review,limitations:['No overall readiness/compliance percentage is calculated.','Impact × urgency is an owner-supplied ordering heuristic, not a calibrated risk model.','A recorded MET state does not certify legal compliance or authorize deployment/purchase.']};
  }
  function markdown(plan,modules,today){
    const s=summary(plan,modules,today),lines=['# Organization decision report','',plan.scale+' · '+plan.organization_type,'','**HUMAN DECISION REQUIRED**',''];
    if(plan.is_synthetic)lines.push('**SYNTHETIC DEMONSTRATION — no real organization was assessed.**','');
    lines.push('## Evidence states','',...states.map(x=>'- '+x+': '+(s.counts[x]||0)),'','## Action queue','');
    for(const a of s.actions)lines.push('- '+a.priority+' · '+a.id+': '+a.action+' | Owner: '+a.owner+' | Target: '+a.target_date);
    for(const m of plan.requirements){lines.push('','## '+m.title+' · '+m.assessment,'','Rationale: '+(m.rationale||'Not established'),'Acceptance criteria: '+(m.acceptance||'Define before testing'),'Acceptance evidence: '+(m.acceptance_evidence||'Not recorded'));
      for(const e of m.evidence||[]){lines.push('','- '+e.reference+' · '+e.locator+' · checked '+e.checked_on+': '+e.finding);if(e.url)lines.push('  Source: '+e.url);}
      if(m.reviewer)lines.push('Reviewer role: '+m.reviewer+' · '+(m.reviewed_on||'NOT_RECORDED'));
    }
    lines.push('','## Review limits and unresolved items','',...[...s.review.warnings,...s.limitations].map(x=>'- '+x));return lines.join('\n')+'\n';
  }
  function html(plan,modules,today){
    const s=summary(plan,modules,today),h=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    let out='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Organization decision report</title><style>body{font:16px/1.6 system-ui,sans-serif;color:#193d31;max-width:1000px;margin:40px auto;padding:0 24px}h1,h2{line-height:1.25}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #ccd7cb;padding:10px;text-align:left;vertical-align:top}th{background:#edf2e7}section{border-top:1px solid #ccd7cb;padding:20px 0}a{overflow-wrap:anywhere}.notice{background:#fff0de;padding:16px}@media print{body{margin:0}h2{break-after:avoid}tr{break-inside:avoid}}</style><h1>Organization decision report</h1><p>'+h(plan.scale)+' · '+h(plan.organization_type)+'</p><p><b>HUMAN DECISION REQUIRED</b></p>';
    if(plan.is_synthetic)out+='<p class="notice"><b>SYNTHETIC DEMONSTRATION — no real organization was assessed.</b></p>';
    out+='<h2>Evidence states</h2><p>'+states.map(k=>h(k)+': '+(s.counts[k]||0)).join(' · ')+'</p><h2>Action queue</h2><table><thead><tr><th>Priority</th><th>Action</th><th>Owner</th><th>Target</th></tr></thead><tbody>';
    for(const a of s.actions)out+='<tr>'+[a.priority,a.title+': '+a.action,a.owner,a.target_date].map(x=>'<td>'+h(x)+'</td>').join('')+'</tr>';
    out+='</tbody></table>';
    for(const m of plan.requirements){out+='<section><h2>'+h(m.title)+' · '+h(m.assessment)+'</h2><p><b>Rationale:</b> '+h(m.rationale||'Not established')+'</p><p><b>Acceptance criteria:</b> '+h(m.acceptance||'Define before testing')+'</p><p><b>Acceptance evidence:</b> '+h(m.acceptance_evidence||'Not recorded')+'</p>';
      for(const e of m.evidence||[]){out+='<p>'+h(e.reference)+' · '+h(e.locator)+' · checked '+h(e.checked_on)+'<br>'+h(e.finding)+'</p>';if(e.url)out+='<p><a href="'+h(e.url)+'">'+h(e.url)+'</a></p>';}
      if(m.reviewer)out+='<p>Reviewer role: '+h(m.reviewer)+' · '+h(m.reviewed_on||'NOT_RECORDED')+'</p>';out+='</section>';
    }
    return out+'<h2>Review limits and unresolved items</h2><ul>'+[...s.review.warnings,...s.limitations].map(x=>'<li>'+h(x)+'</li>').join('')+'</ul></html>\n';
  }
  const api={states,validate,summary,markdown,html};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.DharmaAssessment=api;
})(typeof window==='undefined'?globalThis:window);
