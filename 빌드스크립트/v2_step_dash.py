# -*- coding: utf-8 -*-
# build_v2.py 끝에서 exec (안전보건 단계 뒤, 새 화면 단계 앞) — 📊 대시보드 > 오늘의 할 일
# 05_오늘의할일.html 만들기 + 통합메뉴 맨 위에 대시보드 + 새로고침 · 로그인 · 계정 전환 때 항상 오늘의 할 일부터
import io as _io, os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))

# ===== 1) 05_오늘의할일.html =====
tpl = _io.open(_os.path.join(_HERE, 'v2_dashboard.html'), encoding='utf-8').read()
assert tpl.count('<!--V2HEAD-->') == 1
wr('05_오늘의할일.html', tpl.replace('<!--V2HEAD-->', GATE + COMMON + HEADER))

# ===== 2) 01_통합메뉴 =====
mp = _os.path.join(OUT, '01_통합메뉴.html')
m = _io.open(mp, encoding='utf-8').read().replace('\r\n', '\n')
m = rep(m, "const MENU=[\n  {ic:'🏢', label:'건물관리'",
        "const MENU=[\n  {ic:'📊', label:'대시보드', tag:'keep', perm:'*', kids:[   /* 모든 계정 */\n"
        "    {label:'오늘의 할 일', full:'오늘의 할 일', tag:'keep', link:'05_오늘의할일.html'},\n  ]},\n  {ic:'🏢', label:'건물관리'")
m = rep(m, "function leafVisible(m,k){ if(v2Perm(m.perm||m.label)==='none') return false;",
        "function leafVisible(m,k){ if(m.perm==='*') return true;   /* 대시보드는 모든 계정 */\n  if(v2Perm(m.perm||m.label)==='none') return false;")
m = rep(m, "function openFirst(){\n",
        "/* 메뉴 찾기 · 열기 — 오늘의 할 일 [바로가기]가 씀 */\n"
        "function findLeaf(link,tab){ if(tab==='notice') tab='plan';   /* 교육 공지는 교육 관리로 합침 */\n"
        "  for(let mi=0;mi<MENU.length;mi++){ const ki=MENU[mi].kids.findIndex(k=>k.link===link&&(!tab||k.tab===tab));\n"
        "  if(ki>=0&&leafVisible(MENU[mi],MENU[mi].kids[ki])) return [mi,ki]; } return null; }\n"
        "window.v2CanOpen=(link,tab)=>!!findLeaf(link,tab);\n"
        "window.v2Open=(link,tab)=>{ const f=findLeaf(link,tab); if(!f) return false;\n"
        "  const g=document.querySelector(`.grp[data-mi=\"${f[0]}\"]`); if(g) g.classList.add('open'); openLeaf(f[0],f[1]); return true; };\n"
        "function openFirst(){\n"
        "  try{ sessionStorage.removeItem('bo_open_safety'); }catch(e){}\n"
        "  const dash=findLeaf('05_오늘의할일.html');   /* 새로고침 · 로그인 · 계정 전환 때 항상 대시보드 > 오늘의 할 일 */\n"
        "  if(dash){ document.querySelectorAll('.grp').forEach(g=>g.classList.toggle('open',+g.dataset.mi===dash[0])); openLeaf(dash[0],dash[1]); return; }\n")
open(mp, 'wb').write(m.replace('\n', '\r\n').encode('utf-8'))
print('대시보드 추가: 05_오늘의할일.html + 메뉴')
