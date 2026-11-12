/* Shared deterministic filtering: no network or private data. */
(function (root) {
  'use strict';
  function filter(rows, query = '', filters = {}) {
    const words = query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    return rows.filter(row => words.every(word => JSON.stringify(row).toLocaleLowerCase().includes(word)) && Object.entries(filters).every(([key, value]) => !value || (Array.isArray(row[key]) ? row[key].includes(value) : row[key] === value)));
  }
  function paginate(rows, page = 0, size = 25) {
    if (!Number.isInteger(page) || page < 0 || !Number.isInteger(size) || size < 1 || size > 100) throw new Error('Invalid page');
    const pages = Math.max(1, Math.ceil(rows.length / size));
    const current = Math.min(page, pages - 1);
    return {records: rows.slice(current * size, (current + 1) * size), page: current, pages, total: rows.length};
  }
  const api = {filter, paginate};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.DharmaLibraryCore = api;
})(typeof window !== 'undefined' ? window : globalThis);
