/* Pure evidence checks shared by the browser and the Node regression suite. */
(function (root) {
  'use strict';
  function safeURL(value) {
    try { const u = new URL(value); return ['https:', 'http:'].includes(u.protocol) && !!u.hostname && !u.username; } catch { return false; }
  }
  function validDate(s) {
    if (typeof s !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return false;
    const d = new Date(s + 'T00:00:00Z'); return Number.isFinite(+d) && d.toISOString().slice(0,10) === s;
  }
  function validate(study, data, asOf = new Date().toISOString().slice(0,10), maxAge = 90) {
    const errors = [], warnings = []; let links = 0;
    if (!study || typeof study !== 'object' || Array.isArray(study)) return {structurally_valid:false, errors:['Study must be an object.'], warnings:[], review_status:'HUMAN_REVIEW_REQUIRED', evidence_links:0};
    for (const k of ['schema_version','id','title','question','reference_period','status']) if (typeof study[k] !== 'string' || !study[k].trim()) errors.push(k + ': non-empty text required');
    if (study.schema_version !== '1.0') errors.push('schema_version must be 1.0');
    if (!['draft','desk_review','field_review'].includes(study.status)) errors.push('Unsupported status; no automatic verified state.');
    const geo = study.geography || {};
    if (geo.country !== 'Nepal' || !geo.name || !['national','province','district','municipality','ward','institution'].includes(geo.level)) errors.push('Explicit Nepal geography required.');
    if (geo.level !== 'national' && !geo.code_source_url) warnings.push('Local identity/boundary needs an owning-source link.');
    if (geo.code_source_url && !safeURL(geo.code_source_url)) errors.push('Invalid geographic source URL.');
    for (const field of ['protocol','questions','limitations','next_actions']) if(field in study && (!Array.isArray(study[field]) || study[field].some(x=>typeof x !== 'string'))) errors.push(field + ': list of text entries required');
    if (!Array.isArray(study.domain_ids) || !study.domain_ids.length || study.domain_ids.some(id => !data.domains.some(d => d.id === id))) errors.push('Known domain IDs required.');
    let claims = study.claims;
    if (!Array.isArray(claims)) { errors.push('claims must be a list'); claims=[]; }
    if (!claims.length) warnings.push('No claims/evidence yet. This is a research plan, not a finding.');
    if (claims.length > 500) { errors.push('At most 500 claims per study; split larger artifacts.'); claims=claims.slice(0,500); }
    const ids = claims.filter(c => c && typeof c === 'object').map(c => c.id);
    if (new Set(ids).size !== ids.length || ids.some(id => typeof id !== 'string' || !id)) errors.push('Unique non-empty claim IDs required.');
    claims.forEach((c,i) => {
      const p = 'claims[' + i + ']';
      if (!c || typeof c !== 'object' || Array.isArray(c)) { errors.push(p + ': object required'); return; }
      if (typeof c.text !== 'string' || !c.text.trim()) errors.push(p + ': claim text required');
      if (!['fact','inference','hypothesis','recommendation'].includes(c.kind)) errors.push(p + ': unsupported claim kind');
      let es = c.evidence || [];
      if (!Array.isArray(es)) { errors.push(p + ': evidence must be a list'); es=[]; }
      if (c.kind === 'fact' && !es.some(e => e && e.relation === 'supports')) errors.push(p + ': fact needs supporting evidence');
      if (['inference','recommendation'].includes(c.kind) && (!Array.isArray(c.basis) || !c.basis.length)) errors.push(p + ': basis claim IDs required');
      if (c.basis && (!Array.isArray(c.basis) || c.basis.some(b => !ids.includes(b) || b === c.id))) errors.push(p + ': invalid basis');
      if (!c.limitations) warnings.push(p + ': explain uncertainty/limitations');
      if (c.kind === 'hypothesis') warnings.push(p + ': untested hypothesis');
      es.forEach((e,j) => {
        const ep = p + '.evidence[' + j + ']';
        if (!e || typeof e !== 'object' || Array.isArray(e)) { errors.push(ep + ': object required'); return; }
        const source = data.sources.find(s => s.id === e.source_id);
        if (!source || !safeURL(source.url)) errors.push(ep + ': known source with HTTP(S) URL required');
        if(source?.supported_evidence_levels?.length===1 && source.supported_evidence_levels[0]==='national' && !['Nepal','Nepal national'].includes(e.geography)) errors.push(ep + ': registered national-only source cannot be relabelled as local');
        for (const f of ['locator','reference_period','geography']) if (typeof e[f] !== 'string' || !e[f].trim()) errors.push(ep + ': ' + f + ' required');
        if (!['supports','contradicts','context'].includes(e.relation)) errors.push(ep + ': invalid evidence relation');
        if (e.relation === 'contradicts') warnings.push(ep + ': reconcile contradictory evidence');
        if (!validDate(e.checked_on) || e.checked_on > asOf) errors.push(ep + ': valid non-future check date required');
        else if ((new Date(asOf) - new Date(e.checked_on)) / 86400000 > maxAge) warnings.push(ep + ': older than freshness threshold; assess intended use');
        if (geo.level !== 'national' && e.geography !== geo.name) warnings.push(ep + ': geographic mismatch; no automatic local inference');
        links++;
      });
    });
    const graph = new Map(claims.filter(c => c && typeof c.id === 'string').map(c => [c.id, Array.isArray(c.basis) ? c.basis : []]));
    function cyclic() {
      const active=new Set(),done=new Set();
      for(const root of graph.keys()) {
        const stack=[[root,false]];
        while(stack.length) {
          const [key,exiting]=stack.pop();
          if(exiting) {active.delete(key);done.add(key);continue;}
          if(active.has(key)) return true;
          if(done.has(key)) continue;
          active.add(key);stack.push([key,true]);
          for(const b of graph.get(key)) if(graph.has(b)) stack.push([b,false]);
        }
      }
      return false;
    }
    if (cyclic()) errors.push('Circular claim basis');
    return {structurally_valid:!errors.length, errors,warnings,review_status:'HUMAN_REVIEW_REQUIRED',evidence_links:links};
  }
  function createStudy(template, question, locality) {
    return {schema_version:'1.0',id:'my-study',title:question,question,audience:template.audience,domain_ids:template.domain_ids,
      geography:{country:'Nepal',level:locality === 'Nepal' ? 'national' : 'municipality',name:locality},reference_period:'TO_BE_ESTABLISHED',status:'draft',template_id:template.id,
      protocol:template.steps,questions:template.questions,claims:[],limitations:['Locality, period and baseline require verification.'],next_actions:template.deliverables};
  }
  function markdown(study,data) {
    const lines=['# '+study.title,'','Question: '+study.question,'','Status: '+study.status+' · Period: '+study.reference_period,'Geography: '+study.geography.name,'','**Research artifact — human source and method review required.**',''];
    for(const c of study.claims) {
      lines.push('## '+c.id+' · '+c.kind,'',c.text,'');
      if(c.basis?.length) lines.push('Basis: '+c.basis.join(', '),'');
      for(const e of (c.evidence||[])) { const s=data.sources.find(s=>s.id===e.source_id); lines.push('- '+e.relation+': ['+s.title+']('+s.url+'); '+e.locator+'; period '+e.reference_period+'; geography '+e.geography+'; checked '+e.checked_on+'.'); }
      lines.push('','Limitations: '+(c.limitations||'Not supplied'),'');
    }
    for(const [key,title] of [['protocol','Protocol'],['questions','Questions'],['limitations','Study limitations'],['next_actions','Next actions']]) if(study[key]?.length) lines.push('## '+title,'',...study[key].map(x=>'- '+x),'');
    const check=validate(study,data);
    lines.push('## Structural review','','Errors: '+check.errors.length,'',...check.errors.map(x=>'- ERROR: '+x),...check.warnings.map(x=>'- REVIEW: '+x),'','Checks structure, not truth, representativeness, legal compliance or peer review. Human review is required.','');
    return lines.join('\n');
  }
  const api={safeURL,validDate,validate,createStudy,markdown};
  if(typeof module !== 'undefined' && module.exports) module.exports=api; else root.DharmaCore=api;
})(typeof window === 'undefined' ? globalThis : window);
