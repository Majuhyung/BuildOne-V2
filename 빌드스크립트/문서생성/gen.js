// node gen.js [출력 폴더] [모듈들…]  — 예: node gen.js out dash bld safe
const path = require('path');
const fs = require('fs');
const { build } = require('./lib');
const out = process.argv[2] || 'out';
const want = process.argv.slice(3);
fs.mkdirSync(out, { recursive: true });
const MODS = {
  dash: ['대시보드', './doc_dash'],
  bld: ['건물관리', './doc_bld'],
  safe: ['안전보건', './doc_safe'],
};
(async () => {
  for (const [k, [name, mod]] of Object.entries(MODS)) {
    const sel = want.find(w => w === k || w.startsWith(k + ':'));   // 예: safe  /  safe:dev  /  safe:easy
    if (want.length && !sel) continue;
    const only = sel && sel.includes(':') ? sel.split(':')[1] : '';
    const m = require(mod);
    if (!only || only === 'easy') await build(path.join(out, `BuildOne2_${name}_기획서.docx`), `BuildOne 2.0 ${name} 기획서`, m.easy);
    if (!only || only === 'dev') await build(path.join(out, `BuildOne2_${name}_개발기획서.docx`), `BuildOne 2.0 ${name} 개발 기획서`, m.dev);
    console.log('made', name);
  }
})().catch(e => { console.error(e); process.exit(1); });
