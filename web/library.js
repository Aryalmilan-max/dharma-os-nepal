(function () {
  'use strict';
  const data = window.DHARMA_LIBRARY;
  const core = window.DharmaLibraryCore;
  const $ = id => document.getElementById(id);
  let page = 0;
  function element(tag, text) { const node = document.createElement(tag); node.textContent = text; return node; }
  function options(id, values, caption) {
    const select = $(id); select.replaceChildren();
    const all = element('option', caption); all.value = ''; select.append(all);
    [...new Set(values)].sort().forEach(value => { const option = element('option', value); option.value = value; select.append(option); });
  }
  function reset() {
    const skills = $('mode').value === 'skills'; page = 0;
    options('filter', skills ? data.summary.families : data.sources.map(s => s.kind), 'All');
    options('topic', skills ? [] : data.sources.flatMap(s => s.topics), 'All topics');
    options('publisher', skills ? [] : data.sources.map(s => s.publisher), 'All publishers');
    $('topic').disabled = skills; $('publisher').disabled = skills;
    render();
  }
  function render() {
    const skills = $('mode').value === 'skills';
    const filtered = core.filter(skills ? data.skills : data.sources, $('query').value,
      skills ? {family: $('filter').value} : {kind: $('filter').value, topics: $('topic').value, publisher: $('publisher').value});
    const result = core.paginate(filtered, page); page = result.page;
    $('status').textContent = `${result.total.toLocaleString()} matches · showing at most 25 at a time`;
    $('page').textContent = `Page ${page + 1} of ${result.pages}`;
    $('previous').disabled = page === 0; $('next').disabled = page + 1 >= result.pages;
    const container = $('results'); container.replaceChildren();
    result.records.forEach(item => {
      const card = element('article', ''); card.className = 'hero-note';
      const heading = element('h2', ''); const link = element('a', skills ? item.title : item.label);
      link.href = skills ? '../' + item.path : item.url;
      if (!skills) { link.target = '_blank'; link.rel = 'noopener noreferrer'; }
      heading.append(link); card.append(heading);
      if (skills) {
        card.append(element('p', `${item.family} · ${item.id}`), element('p', item.trigger), element('p', `Acceptance: ${item.acceptance}`));
        const template = element('a', 'Open blank working record (CSV)'); template.href = `../skills/${item.id}/assets/working-record.csv`; card.append(template);
      } else {
        card.append(element('p', `${item.publisher} · ${item.kind}`), element('p', item.verification_state), element('p', item.applicability), element('p', item.url));
        if (item.label_basis === 'URL_DERIVED_NOT_RETRIEVED_PAGE_TITLE') card.append(element('small', 'Navigation label derived from URL; page title not retrieved.'));
      }
      container.append(card);
    });
    if (!result.total) container.append(element('p', 'No matches. Try fewer words or clear a filter.'));
  }
  $('counts').textContent = `${data.summary.task_skills} focused task skills + 1 Dharma OS router. ${data.sources.length.toLocaleString()} distinct reference URLs. Each task has its own working record and acceptance check.`;
  $('mode').addEventListener('change', reset);
  ['query', 'filter', 'topic', 'publisher'].forEach(id => $(id).addEventListener('input', () => { page = 0; render(); }));
  $('previous').addEventListener('click', () => { page -= 1; render(); });
  $('next').addEventListener('click', () => { page += 1; render(); });
  reset();
})();
