# -*- coding: utf-8 -*-
# build_v2.py 끝에서 exec — 안전보건(V1 27_안전보건)을 V2에 그대로: 04_안전보건.html + 통합메뉴 안전보건 그룹
# (rd / wr / rep / cut / OUT / SRC / GATE / COMMON / HEADER 를 build_v2.py에서 그대로 씀)
import io as _io, os as _os

# ===== 1) 04_안전보건.html =====
s = rd('27_안전보건.html')
s = rep(s, '<head>', '<head>\n' + GATE + COMMON + HEADER, 1)
s = rep(s, '<header><div class="logo">BuildOne <small id="hdrBld">', '<header class="v2top"><div class="logo">BuildOne <small id="hdrBld">')
s = s.replace('<title>BuildOne — 안전보건관리</title>', '<title>BuildOne 2.0 — 안전보건관리</title>')
# 시연 계정 전환 때 V2 메뉴 권한(buildone_perm)도 그 역할로
s = rep(s, "    localStorage.setItem('buildone_user',a.name+' · '+a.role);\n    if(Array.isArray(a.buildings)){",
        "    localStorage.setItem('buildone_user',a.name+' · '+a.role);\n"
        "    try{ localStorage.setItem('buildone_perm',JSON.stringify(boEnsureRoles()[a.role]||{})); }catch(e){}   /* V2: 메뉴 권한도 그 역할로 */\n"
        "    if(Array.isArray(a.buildings)){")
s = rep(s, '</body>', "<script>/* V2 — 안전보건 메뉴 권한이 없으면 차단 (화면 안 기능은 원래 역할 규칙 그대로) */\n"
        "if(v2Perm('안전보건')==='none') v2Deny('안전보건');\n</script>\n</body>")
# ---- V2: 안전보건은 6개 화면만 (교육 공지 · 위험성평가 · 나의 안전보건 리스트 · 안전교육 리스트 · 위험성평가 리스트 · 경영책임자 현황) ----
s = rep(s, "const tabOk=t=>MY.tabs==='*'||MY.tabs.includes(t);",
        "const V2_DROP=['policy','status','permit','patrol','review','audit'];   /* V2에서 뺀 화면 — 메뉴 · 바로가기 · 주소(#)로도 열리지 않음 (교육 계획 · 실시는 다시 넣음) */\n"
        "const tabOk=t=>!V2_DROP.includes(t)&&(MY.tabs==='*'||MY.tabs.includes(t));")
PRUNE = r'''<script>/* V2 — 뺀 화면으로 가는 [보기] 버튼 · 바로가기 줄 숨김 (화면 안 메뉴에서도 뺌) */
document.querySelectorAll('.tabs button').forEach(b=>{ if(V2_DROP.includes(b.dataset.t)) b.remove(); });
function v2Prune(){
  document.querySelectorAll('[onclick*="goTab("]').forEach(el=>{ const m=(el.getAttribute('onclick')||'').match(/goTab\('([a-z]+)'/);
    if(m&&V2_DROP.includes(m[1])){ const li=el.closest('ul.todo li'); if(li) li.remove(); else el.remove(); } });
  document.querySelectorAll('a[href^="#"]').forEach(a=>{ if(V2_DROP.includes(a.getAttribute('href').slice(1))) a.remove(); });   /* 예: 결재하러 가기(#review) */
  document.querySelectorAll('ul.todo').forEach(u=>{ if(!u.children.length) u.innerHTML='<li><span class="ic">✅</span><span class="tx">처리할 항목이 없습니다.</span></li>'; });
}
const v2RenderAll=renderAll; renderAll=function(){ v2RenderAll.apply(this,arguments); v2Prune(); }; v2Prune();
if(!tabOk(curTab)) switchTab(MY.home||'ceo');
</script>
'''
s = rep(s, '</body>', PRUNE + '</body>')
HALF = r"""<script>/* V2 — [반기]를 위쪽 [건물] 바로 옆으로 */
function v2MoveHalf(){ const bar=document.querySelector('.bo-ctxbar .bo-bld'), hs=document.getElementById('halfSel'); if(!bar||!hs) return;
  const lb=hs.previousElementSibling; const sp=document.createElement('span'); sp.style.width='14px';
  bar.after(sp); if(lb&&lb.tagName==='LABEL'){ lb.style.marginLeft='0'; sp.after(lb); lb.after(hs); } else sp.after(hs);
  const cd=document.querySelector('.cond'); if(cd&&!cd.contains(hs)) cd.style.display='none';   /* 남은 '…기준' 안내 줄은 뺌 */
}
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',v2MoveHalf); else v2MoveHalf();   /* 건물 줄이 만들어진 뒤 */
</script>
"""
ALL = r"""<script>/* V2 — 건물 목록 맨 위 [전체] */
function v2PickBld(code){ const i=BUILDINGS.findIndex(b=>b.code===code); if(i<0) return;
  V2_ALL=false;
  curBld=i; localStorage.setItem('buildone_current_building',gIdx(i)); const cb=document.querySelector('.bo-ctxbar .bo-bld'); if(cb) cb.value=gIdx(i); renderBldSel(); renderAll(); }
function v2ScopeText(){ const a=V2_ALL?'전체 건물':'선택 건물';
  document.querySelectorAll('.v2scope').forEach(e=>{ e.textContent=a; });
  const h=document.getElementById('scopeHint'), sc=SCOPE[curTab]||'';   /* 전체면 '선택 건물 · 우리 건물 기준' → '전체 건물 기준' */
  if(h) h.textContent=V2_ALL&&(/선택 건물/.test(sc)||(/우리 건물/.test(sc)&&!myLinked()))?'전체 건물 기준':sc; }
const v2RA2=renderAll; renderAll=function(){ v2RA2.apply(this,arguments); v2ScopeText(); };
const v2Sw=switchTab; switchTab=function(){ v2Sw.apply(this,arguments); v2ScopeText(); };
const v2GoTab=window.goTab; window.goTab=(t,code)=>{ if(code&&V2_ALL) v2PickBld(code); return v2GoTab(t,code); };   /* 바로가기로 특정 건물을 열면 그 건물로 */
/* [전체]일 때: 새로 등록 · 건물 단위 출력은 한 건물을 고른 뒤 / 줄의 [수정] · [완료]는 그 건물로 바꾼 뒤 바로 실행 */
const V2_NEEDONE=['btnAddRisk','btnRiskPrint','btnIncident'];
document.addEventListener('click',e=>{ if(!V2_ALL) return; const el=e.target.closest('button,a,[onclick]'); if(!el) return; const oc=el.getAttribute('onclick')||'';
  if(V2_NEEDONE.includes(el.id)||/^recordEval\(/.test(oc)){ e.stopPropagation(); e.preventDefault(); toast('위쪽 [건물]에서 건물을 하나 고른 뒤 사용하세요','warn'); return; }
  const m=oc.match(/^(editSess|cancelSess|editRisk|doneRisk|doneIncident)\('([^']+)'\)/);
  if(m){ const code=v2CodeOf(m[2]); if(!code) return; e.stopPropagation(); e.preventDefault(); v2PickBld(code); window[m[1]](m[2]); } },true);
function v2AllSetup(){ const sel=document.querySelector('.bo-ctxbar .bo-bld'); if(!sel||BUILDINGS.length<2){ if(V2_ALL){ V2_ALL=false; renderAll(); } return; }   /* 건물이 하나뿐인 계정은 전체 없음 */
  sel.insertAdjacentHTML('afterbegin','<option value="all">전체</option>'); if(V2_ALL) sel.value='all';
  sel.parentNode.addEventListener('change',e=>{ if(e.target!==sel) return; const all=sel.value==='all';
    V2_ALL=all;
    if(all){ e.stopPropagation(); renderAll(); } else setTimeout(renderAll,0); },true);   /* 전체는 공유 건물 값을 건드리지 않음 */
  v2ScopeText(); }
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',v2AllSetup); else v2AllSetup();
</script>
"""
s = rep(s, '</body>', ALL + '</body>')
s = rep(s, '</body>', HALF + '</body>')
# 화면 안 메뉴(단독으로 열 때)도 '나의 안전보건'을 맨 앞에
s = rep(s, '  <button data-t="notice">교육 공지 · 서명 현황</button>\n  <button data-t="my">나의 안전보건 리스트</button>\n',
        '  <button data-t="my">나의 안전보건</button>\n  <button data-t="notice">교육 공지 · 서명 현황</button>\n')
# 교육 공지 · 서명 현황, 위험성평가는 선택한 건물만 (다른 건물 줄 · 합계가 섞이지 않게)
s = rep(s, "  BUILDINGS.forEach(b=>B(b.code).sessions.filter(x=>x.method==='공지'&&x.status!=='cancelled').forEach(x=>{ const k=x.nid||x.id; (g[k]=g[k]||[]).push(x); }));",
        "  BUILDINGS.filter(b=>b.code===bldKey()).forEach(b=>B(b.code).sessions.filter(x=>x.method==='공지'&&x.status!=='cancelled').forEach(x=>{ const k=x.nid||x.id; (g[k]=g[k]||[]).push(x); }));   /* V2: 선택 건물만 */")
s = rep(s, "function renderMeetings(){\n  const rows=BUILDINGS.map(b=>({b,st:meetStat(b.code)}));",
        "function renderMeetings(){\n  const rows=BUILDINGS.filter(b=>b.code===bldKey()).map(b=>({b,st:meetStat(b.code)}));   /* V2: 선택 건물만 */")
s = rep(s, "<h3>사업장별 위험성평가 회의 현황 <small>", "<h3>위험성평가 회의 현황 <small>· 선택 건물 ")
s = rep(s, "['1년 안에 회의한 사업장',", "['1년 안에 정기 회의',")
s = rep(s, "notice:'전 사업장 기준'", "notice:'선택 건물 기준'")
# 나의 안전보건 · 안전교육 리스트 · 위험성평가 리스트: 장소는 그 건물의 지금 이름으로
#   (시연 자료 장소에 들어 있는 처음 건물 이름 '대성빌딩 로비' → '플랫폼포지 (관악) 로비')
_a = s.index('function renderMine(){'); _b = s.index('/* 교육 읽기 → 서명 (공지 · 경영방침 공용) */')
_seg = s[_a:_b]
_seg = _seg.replace("esc(x.place||'-')", "esc(placeName(x.place,code0(x))||'-')").replace("esc(m.place)", "esc(placeName(m.place,code0(m)))")
PLACE_FN = r'''/* V2 — 장소 표시: 시연 자료를 만들 때의 건물 이름을 그 건물의 지금 이름(지점 포함)으로 바꿔 보여 줌 */
const V2_SEEDNAME={D0517:'대성빌딩',D0662:'대성2빌딩'};
const code0=o=>(o&&(o.bld||(o.targets&&o.targets[0]&&String(o.targets[0]).split(':')[0])))||bldKey();
function placeName(p,code){ p=p||''; const seed=V2_SEEDNAME[code], b=ALLB.find(x=>x.code===code); if(!seed||!b||!p.includes(seed)) return p;
  return b.name===seed?p:p.split(seed).join(b.name); }
'''
s = s[:_a] + PLACE_FN + _seg + s[_b:]
assert s.count('placeName(') >= 6
# ---- V2: 건물 목록에 [전체] — 모든 건물을 한 화면에 (건물 이름을 붙여서) ----
s = rep(s, "function bldKey(){ return (BUILDINGS[curBld]||{}).code||'default'; }",
r"""let V2_ALL=true, V2_AT=null;   /* V2: 건물은 열 때마다 항상 [전체] · V2_AT = 잠깐 한 건물로 그릴 때 */
function bldKey(){ return V2_AT||(BUILDINGS[curBld]||{}).code||'default'; }
const V2_RC={};   /* 위험요인 id → 건물 */
function v2FieldAll(){ const o={risks:[],open:[],highOpen:[]}; BUILDINGS.forEach(b=>{ const f=fieldStats(b.code); f.risks.forEach(r=>{ V2_RC[r.id]=b.code; });
  o.risks.push(...f.risks); o.open.push(...f.open); o.highOpen.push(...f.highOpen); }); return o; }
function v2Ws(){ return V2_ALL?BUILDINGS.flatMap(b=>workers(b.code)):workers(bldKey()); }
function v2CodeOf(id){ if(V2_RC[id]) return V2_RC[id]; for(const b of BUILDINGS){ const x=B(b.code);
  if((x.sessions||[]).some(o=>o.id===id)||(x.risks||[]).some(o=>o.id===id)||(x.incidents||[]).some(o=>o.id===id)) return b.code; } return null; }""")
# 교육 공지 · 위험성평가 회의 현황: 전체면 모든 건물
s = rep(s, "BUILDINGS.filter(b=>b.code===bldKey())", "BUILDINGS.filter(b=>V2_ALL||b.code===bldKey())", 2)
_a = s.index('function renderMeetings(){'); _b = s.index('/* 회의 기록 보기 */')
s = s[:_a] + rep(s[_a:_b], "<tr class=\"${b.code===bldKey()?'cur':''}\">", "<tr class=\"${!V2_ALL&&b.code===bldKey()?'cur':''}\">") + s[_b:]
s = rep(s, "<h3>위험성평가 회의 현황 <small>· 선택 건물 ", "<h3>위험성평가 회의 현황 <small>· <span class=\"v2scope\">선택 건물</span> ")
# 교육 계획 · 실시
s = rep(s, "const all=B(code).sessions.filter(s=>s.date>=H.start&&s.date<=H.end);",
        "const all=(V2_ALL?BUILDINGS.flatMap(b=>B(b.code).sessions):B(code).sessions).filter(s=>s.date>=H.start&&s.date<=H.end);")
s = rep(s, "['사업장',esc(bldName(code)),H.label]", "['사업장',V2_ALL?'전체 '+BUILDINGS.length+'곳':esc(bldName(code)),H.label]")
s = rep(s, "<td class=\"left\">${esc(s.title)}${cx?", "<td class=\"left\">${V2_ALL?`<small class=\"hint\">${esc(bldName(s.bld))}</small><br>`:''}${esc(s.title)}${cx?")
# 위험성평가 (회의 기록 · 위험요인 표)
_a = s.index('function renderRisk(){'); _b = s.index('window.showImg=')
_seg = s[_a:_b]
for _o, _n in [
    ("fs=fieldStats(code), f=", "fs=V2_ALL?v2FieldAll():fieldStats(code), f="),
    ("const ml=meetsOf(code).filter(", "const ml=(V2_ALL?BUILDINGS.flatMap(b=>meetsOf(b.code)):meetsOf(code)).filter("),
    ("<h3>${esc(bldName(code))} — 위험성평가 회의 기록</h3>", "<h3>${V2_ALL?'전체 건물':esc(bldName(code))} — 위험성평가 회의 기록</h3>"),
    ("<td class=\"left\">${esc(m.title)}</td>", "<td class=\"left\">${V2_ALL?`<small class=\"hint\">${esc(bldName(m.bld))}</small> `:''}${esc(m.title)}</td>"),
    ("<td class=\"left\">${r.proc?", "<td class=\"left\">${V2_ALL?`<b>${esc(bldName(V2_RC[r.id]))}</b><br>`:''}${r.proc?"),
]:
    assert _seg.count(_o) == 1, _o
    _seg = _seg.replace(_o, _n)
s = s[:_a] + _seg + s[_b:]
# 교육 계획 · 실시: [+ 교육 등록]을 줄 오른쪽 끝으로
s = rep(s, '      <button class="btn sm" id="btnAddSess">+ 교육 등록</button>\n      <label style="margin-left:6px">교육 종류</label>\n'
           '      <select id="pType"><option value="">전체</option></select>\n      <div class="spacer"></div>\n'
           '      <span class="hint" style="margin:0">교육은 삭제되지 않고 ‘취소’로만 처리되며, 수정 내용은 기록 이력에 남습니다</span>\n',
        '      <label>교육 종류</label>\n'
        '      <select id="pType"><option value="">전체</option></select>\n      <div class="spacer"></div>\n'
        '      <span class="hint" style="margin:0">교육은 삭제되지 않고 ‘취소’로만 처리되며, 수정 내용은 기록 이력에 남습니다</span>\n'
        '      <button class="btn sm" id="btnAddSess" style="margin-left:auto">+ 교육 등록</button>\n')
# 경영책임자 현황은 대표만 (관리자 · 이사 · 총무도 안 보임) · 대표는 이 화면부터
s = rep(s, "const MYROLE=", "/* V2 — 경영책임자 현황은 대표만 */\n"
        "Object.keys(SR).forEach(r=>{ if(r==='대표') return; if(Array.isArray(SR[r].tabs)) SR[r].tabs=SR[r].tabs.filter(x=>x!=='ceo'); if(SR[r].home==='ceo') SR[r].home='notice'; }); SR['대표'].home='ceo';\n"
        "const MYROLE=")
s = rep(s, "const tabOk=t=>!V2_DROP.includes(t)&&", "const tabOk=t=>!V2_DROP.includes(t)&&(t!=='ceo'||MYROLE==='대표')&&")
_m = __import__('re').search(r'  <button data-t="ceo"[^\n]*\n', s); assert _m
s = s.replace(_m.group(0), '', 1)
s = rep(s, '  <button data-t="my">나의 안전보건</button>\n', _m.group(0) + '  <button data-t="my">나의 안전보건</button>\n')
# 교육 등록: 총무 · 이사 · 대표 · 관리자만(대표에게 plan 권한 추가) · 새 교육은 회사 모든 직원(접근 건물 전체)이 대상
s = rep(s, "SR['대표'].home='ceo';\n", "SR['대표'].home='ceo'; if(!SR['대표'].can.includes('plan')) SR['대표'].can.push('plan');   /* V2: 교육 등록은 총무 · 이사 · 대표 · 관리자 */\n")
s = rep(s, "  sEditId=s?s.id:null; const p=s||preset||{}; const ws=workers(bldKey());\n"
           "  document.getElementById('sDlgMode').textContent=s?'교육 수정':'교육 등록';\n"
           "  document.getElementById('sDlgSub').textContent='· '+bldName(bldKey());\n",
        "  sEditId=s?s.id:null; const p=s||preset||{};\n"
        "  const ws=s?workers(s.bld):BUILDINGS.flatMap(b=>workers(b.code)); V2_SWS=ws;   /* V2: 새 교육 = 회사 모든 직원 · 수정 = 그 건물 */\n"
        "  document.getElementById('sDlgMode').textContent=s?'교육 수정':'교육 등록';\n"
        "  document.getElementById('sDlgSub').textContent=s?'· '+bldName(s.bld):`· 회사 전체 직원 ${ws.length}명 (${BUILDINGS.length}개 건물)`;\n")
s = rep(s, "  const tg=new Set(p.targets||defTargets(type,ws));\n"
           "  document.getElementById('s_targets').innerHTML=ws.length? ws.map(w=>`<label><input type=\"checkbox\" value=\"${w.key}\" data-role=\"${w.role}\" ${tg.has(w.key)?'checked':''}> ${esc(w.name)} <small>${ROLE[w.role].name}</small></label>`).join('')\n",
        "  const tg=new Set(p.targets||(s?defTargets(type,ws):ws.map(w=>w.key)));   /* 새 교육은 모든 직원을 기본 선택 */\n"
        "  document.getElementById('s_targets').innerHTML=ws.length? (s?[s.bld]:BUILDINGS.map(b=>b.code)).map(c=>{ const g=ws.filter(w=>w.bld===c); if(!g.length) return '';\n"
        "      return (s?'':`<div style=\"grid-column:1/-1;font-weight:700;font-size:12.5px;color:#3d4451;margin-top:4px\">🏢 ${esc(bldName(c))} <small style=\"font-weight:500\">${g.length}명</small></div>`)\n"
        "        +g.map(w=>`<label><input type=\"checkbox\" value=\"${w.key}\" data-role=\"${w.role}\" ${tg.has(w.key)?'checked':''}> ${esc(w.name)} <small>${ROLE[w.role].name}</small></label>`).join(''); }).join('')\n")
s = rep(s, "  document.getElementById('s_hours').value=ET[t].h; const tg=new Set(defTargets(t,workers(bldKey())));\n",
        "  const ws=V2_SWS||workers(bldKey()); document.getElementById('s_hours').value=ET[t].h; const tg=new Set(t==='sup'||t==='hire'?defTargets(t,ws):ws.map(w=>w.key));   /* V2: 관리감독자 · 채용 시 교육 말고는 모든 직원 */\n")
s = rep(s, "function defTargets(type,ws){\n", "let V2_SWS=null;   /* 열린 교육 등록 창의 대상 직원 */\nfunction defTargets(type,ws){\n")
# 저장: 대상 직원의 건물마다 한 건씩(같은 묶음 번호 nid) — 건물별 출석 · 서명이 그대로 동작
s = rep(s, "    const s=Object.assign({id:'s'+(S.sseq++),bld:bldKey(),att:{},photos:[],status:'active',createdAt:nowStr(),createdBy:curUser()},v);\n"
           "    B().sessions.push(s);\n"
           "    logA('교육 등록',`${ET[s.type].name} 「${s.title}」 ${s.date} · ${s.hours}시간 · ${s.method} · 대상 ${s.targets.length}명`,s.bld);\n"
           "    saveS(); g('sDlg').close(); renderAll(); toast('교육 등록 완료','ok');\n",
        "    const codes=[...new Set(v.targets.map(k=>k.split(':')[0]))], nid='g'+Date.now(), at=nowStr();\n"
        "    codes.forEach(c=>{ const s=Object.assign({id:'s'+(S.sseq++),bld:c,nid,att:{},photos:[],status:'active',createdAt:at,createdBy:curUser()},v,{targets:v.targets.filter(k=>k.split(':')[0]===c)});\n"
        "      B(c).sessions.push(s);\n"
        "      logA('교육 등록',`${ET[s.type].name} 「${s.title}」 ${s.date} · ${s.hours}시간 · ${s.method} · 대상 ${s.targets.length}명`,c); });\n"
        "    saveS(); g('sDlg').close(); renderAll(); toast(`교육 등록 완료 · ${codes.length}개 건물 ${v.targets.length}명`,'ok');\n")
# ===== 교육 공지 · 서명 현황 + 교육 계획 · 실시 → 하나의 [교육 관리] (한 화면 · 한 목록) =====
# 화면 안 메뉴: 교육 공지 칸을 없애고 그 자리에 교육 관리
s = rep(s, '  <button data-t="plan">교육 계획 · 실시</button>\n', '')
s = rep(s, '  <button data-t="notice">교육 공지 · 서명 현황</button>\n', '  <button data-t="plan">교육 관리</button>\n')
# 예전 주소(#notice) · 바로가기는 교육 관리로
s = rep(s, "function switchTab(t){ if(!tabOk(t))", "function switchTab(t){ if(t==='notice') t='plan';   /* V2: 교육 공지는 교육 관리로 합침 */\n  if(!tabOk(t))")
s = rep(s, "if(h==='mymeet') h='my';", "if(h==='mymeet') h='my'; if(h==='notice') h='plan';")
# 화면 위: 제목 · 설명 · 시연 초기화 / 줄: 교육 종류 · 교육 방법 · [+ 교육 등록]
s = rep(s, '  <section class="page" id="pg-plan">\n    <div class="kpis" id="planKpis"></div>\n    <div class="toolbar">\n      <label>교육 종류</label>\n'
           '      <select id="pType"><option value="">전체</option></select>\n      <div class="spacer"></div>\n'
           '      <span class="hint" style="margin:0">교육은 삭제되지 않고 ‘취소’로만 처리되며, 수정 내용은 기록 이력에 남습니다</span>\n',
        '  <section class="page" id="pg-plan">\n'
        '    <div class="nt-hero"><div class="t"><b>교육 관리</b>\n'
        '      <div class="hint" style="margin:4px 0 0;font-size:12.5px">교육 공지(알림톡 · 휴대폰 서명)와 집합 · 온라인 · 외부위탁 교육을 한 목록에서 등록하고 서명 · 출석을 확인합니다. 교육은 삭제되지 않고 ‘취소’로만 처리되며, 수정 내용은 기록 이력에 남습니다.</div></div>\n'
        '      <div class="nt-acts"><button class="btn ghost sm" onclick="demoReset()" title="시연용 — 교육 공지 · 서명 · 위험성평가 기록을 모두 처음 시연 데이터로">🔄 시연 초기화</button></div></div>\n'
        '    <div class="kpis" id="planKpis"></div>\n    <div class="toolbar">\n      <label>교육 종류</label>\n'
        '      <select id="pType"><option value="">전체</option></select>\n'
        '      <label style="margin-left:6px">교육 방법</label>\n'
        '      <select id="pMethod"><option value="">전체</option><option>집합</option><option>온라인</option><option>외부위탁</option><option>공지</option></select>\n'
        '      <div class="spacer"></div>\n')
s = rep(s, '<th>이수 / 대상</th><th>상태</th><th>처리</th>', '<th>서명 · 출석 / 대상</th><th>상태</th><th>처리</th>')
# 목록 · 합계: 방법 고르기 + 공지 서명 합계
_a = s.index('function renderPlan(){'); _b = s.index('/* 교육 등록/수정 모달 */')
_seg = s[_a:_b]
for _o, _n in [
    ("const list=all.filter(s=>!f||s.type===f)", "const fm=(document.getElementById('pMethod')||{}).value||'', list=all.filter(s=>(!f||s.type===f)&&(!fm||s.method===fm))"),
    ("  document.getElementById('planKpis').innerHTML=[\n",
     "  const dueA=act.filter(s=>s.date<=TODAYS), tT=dueA.reduce((a,s)=>a+s.targets.length,0), tS=dueA.reduce((a,s)=>a+s.targets.filter(k=>s.att[k]).length,0);\n"
     "  const nN=act.filter(s=>s.method==='공지').length, late=act.filter(s=>s.method==='공지'&&s.due&&s.due<TODAYS).reduce((a,s)=>a+s.targets.filter(k=>!s.att[k]).length,0);\n"
     "  document.getElementById('planKpis').innerHTML=[\n"),
    ("    ['교육 실시',act.length+'회',`완료 ${done} · 예정 ${plan}`],['이수 연인원',persons+'명','서명·수강 완료 기준'],\n"
     "    ['누적 교육시간',manH+'시간','인원 × 시간'],['사업장',V2_ALL?'전체 '+BUILDINGS.length+'곳':esc(bldName(code)),H.label],\n",
     "    ['교육 실시',act.length+'회',`완료 ${done} · 예정 ${plan} · 공지 ${nN}건`],\n"
     "    ['서명 · 출석 완료',`<span style=\"color:${barColor(pct(tS,tT))}\">${pct(tS,tT)}%</span>`,`${tS} / ${tT}명 · ${V2_ALL?'전체 '+BUILDINGS.length+'곳':esc(bldName(code))}`],\n"
     "    ['아직 안 한 분',`<span style=\"${tT-tS?'color:var(--warn)':''}\">${tT-tS}명</span>`,late?`<b style=\"color:var(--bad)\">공지 마감 지남 ${late}명</b>`:'마감 지난 공지 없음'],\n"
     "    ['누적 교육시간',manH+'시간',`인원 × 시간 · ${H.label} · 공지는 미산입`],\n"),
    ("${esc(s.title)}${cx?",
     "${esc(s.title)}${s.method==='공지'&&s.due&&!cx?`<br><small class=\"hint\" style=\"${s.due<TODAYS&&n<m?'color:var(--bad);font-weight:700':''}\">서명 마감 ${s.due}${s.due<TODAYS&&n<m?' · 지남':''}</small>`:''}${cx?"),
    ("<button class=\"btn ghost sm\" onclick=\"printSession('${s.id}')\">증빙</button>",
     "${s.method==='공지'&&!cx&&n<m?`<button class=\"btn ghost sm\" onclick=\"remindNotice('${s.id}')\">알림톡 다시</button> `:''}<button class=\"btn ghost sm\" onclick=\"printSession('${s.id}')\">증빙</button>"),
]:
    assert _seg.count(_o) == 1, _o[:60]
    _seg = _seg.replace(_o, _n)
s = s[:_a] + _seg + s[_b:]
# 교육 등록: 방법에 [공지] — 고르면 교육 공지 보내기 창(알림톡 · 서명 마감)으로
s = rep(s, '<select id="s_method"><option>집합</option><option>온라인</option><option>외부위탁</option></select>',
        '<select id="s_method"><option>집합</option><option>온라인</option><option>외부위탁</option><option>공지</option></select>')
s = rep(s, "if(v.hours<=0){", "if(v.hours<=0&&v.method!=='공지'){")   # 공지는 법정 시간 미산입(0시간)
MERGE = r"""<script>/* V2 — 교육 관리(교육 공지 + 교육 계획 · 실시) */
document.getElementById('pMethod').addEventListener('change',renderPlan);
document.getElementById('s_method').addEventListener('change',e=>{ const v=e.target.value;
  if(sEditId){ const s0=findSess(sEditId); if(s0&&s0.method!=='공지'&&v==='공지'){ e.target.value=s0.method; toast('이미 등록한 교육은 공지로 바꿀 수 없습니다 — 새로 등록하세요','warn'); } return; }
  if(v!=='공지') return; e.target.value='집합';
  if(!can('notice')) return deny('교육 공지는 대표 계정이 보냅니다');
  const ti=document.getElementById('s_title').value.trim(); document.getElementById('sDlg').close(); openNoticeDlg();
  if(ti){ document.getElementById('n_title').value=ti; updNotice(); } });
</script>
"""
s = rep(s, '</body>', MERGE + '</body>')
# 교육 관리: [교육 상태] 전체 · 완료 · 미완료 (미완료 = 예정 · 진행중 — 취소는 전체에서만)
s = rep(s, '<option>외부위탁</option><option>공지</option></select>\n      <div class="spacer"></div>\n',
        '<option>외부위탁</option><option>공지</option></select>\n'
        '      <label style="margin-left:6px">교육 상태</label>\n'
        '      <select id="pState"><option value="">전체</option><option value="done">완료</option><option value="todo">미완료</option></select>\n'
        '      <div class="spacer"></div>\n')
s = rep(s, "list=all.filter(s=>(!f||s.type===f)&&(!fm||s.method===fm))",
        "fst=(document.getElementById('pState')||{}).value||'', list=all.filter(s=>(!f||s.type===f)&&(!fm||s.method===fm)"
        "&&(!fst||(fst==='done'?sStatus(s)[0]==='완료':s.status!=='cancelled'&&sStatus(s)[0]!=='완료')))")
s = rep(s, "document.getElementById('pMethod').addEventListener('change',renderPlan);\n",
        "document.getElementById('pMethod').addEventListener('change',renderPlan);\n"
        "document.getElementById('pState').addEventListener('change',renderPlan);\n")
s = rep(s, "${H.label}에 등록된 교육이 없습니다. [+ 교육 등록]으로 추가하세요.",
        "${(f||fm||fst)&&all.length?`${H.label}에 고른 조건(종류 · 방법 · 상태)에 맞는 교육이 없습니다.`:`${H.label}에 등록된 교육이 없습니다. [+ 교육 등록]으로 추가하세요.`}")
# 위험성평가: 회의 전에 뽑는 [회의용 위험성평가표] (검토할 위험요인 + 손으로 적는 칸)
DRAFT_FN = r"""/* V2 — 회의용 위험성평가표: 회의 전에 출력해서 보면서 이야기하고, 정한 점수 · 새 위험 · 의견을 손으로 적음 */
window.printMeetingDraft=id=>{ const m=findMeet(id); if(!m) return; const its=planItems(m), host=empByKey(m.host), blank='<td class="c" style="height:30px"></td>';
  const crit='가능성 1 거의 없음 · 2 가끔 있음 · 3 자주 있음 / 중대성 1 가벼운 부상 · 2 치료 · 휴업 필요 · 3 사망 · 중상 / 위험도 = 가능성 × 중대성 → 높음 6~9 · 보통 3~4 · 낮음 1~2';
  const body=`<h1>위 험 성 평 가 표 (회의용)</h1><div class="psub">${esc(S.company.name)} · ${esc(bldName(m.bld))}</div>
    <table class="pinfo"><tr><th>회의 이름</th><td colspan="3">${esc(m.title)} (${esc(m.kind||'정기')})</td></tr>
      <tr><th>회의 일시</th><td>${m.date} (${dwOf(m.date)}) ${m.start} ~ ${m.end}</td><th>회의 장소</th><td>${esc(placeName(m.place,m.bld))}</td></tr>
      <tr><th>진행</th><td>${esc(host.name)} (관리감독자)</td><th>참석 대상</th><td>${m.targets.length}명</td></tr>
      <tr><th>회의 안건</th><td colspan="3"><ol style="margin:0;padding-left:18px">${(m.agenda||[]).map(a=>`<li>${esc(a)}</li>`).join('')}</ol></td></tr>
      <tr><th>판단 기준</th><td colspan="3">${crit}</td></tr></table>
    <h2>① 검토할 위험요인 <small>· ${its.length}건 · 회의에서 점수를 다시 정하면 오른쪽 칸에 적어 주세요</small></h2>
    <table><tr><th class="c">No</th><th class="c">공정</th><th>장소 · 유해 · 위험요인</th><th>현재 조치</th><th class="c">현재 점수</th><th>감소대책(안)</th><th class="c">회의 결정<br>가능성</th><th class="c">회의 결정<br>중대성</th><th>담당 · 기한</th></tr>
    ${its.length?its.map((r,i)=>`<tr><td class="c">${i+1}</td><td class="c">${esc(r.proc||'공통')}</td><td><b>${esc(r.place)}</b><br>${esc(r.hazard)}</td><td>${esc(r.current||'-')}</td><td class="c">${r.l}×${r.s}<br>${lvOf(r.l*r.s)[0]}</td><td>${esc(r.measure||'')}</td>${blank}${blank}<td></td></tr>`).join('')
      :'<tr><td colspan="9" class="c" style="height:30px">미리 정한 위험요인이 없습니다. 아래 ②에 회의에서 찾은 위험을 적어 주세요.</td></tr>'}</table>
    <h2>② 회의에서 새로 찾은 위험</h2>
    <table><tr><th class="c">No</th><th>장소</th><th>유해 · 위험요인</th><th class="c">가능성</th><th class="c">중대성</th><th>감소대책</th><th>담당 · 기한</th></tr>
    ${[1,2,3,4,5].map(i=>`<tr><td class="c" style="height:30px">${i}</td><td></td><td></td>${blank}${blank}<td></td><td></td></tr>`).join('')}</table>
    <h2>③ 직원 의견</h2><table>${[1,2,3,4].map(()=>'<tr><td style="height:30px"></td></tr>').join('')}</table>
    <h2>④ 참석자 확인 <small>· 휴대폰 서명이 어려운 분만 적어 주세요</small></h2>
    <table><tr><th class="c">No</th><th>성명</th><th class="c">구분</th><th class="c">서명</th></tr>
    ${m.targets.map((k,i)=>{ const w=empByKey(k); return `<tr><td class="c">${i+1}</td><td>${esc(w.name)}</td><td class="c">${ROLE[w.role].name}</td><td class="c" style="height:30px;width:30%"></td></tr>`; }).join('')}</table>`;
  printDoc(body,`위험성평가 회의용 평가표 「${m.title}」`,m.bld); };
"""
s = rep(s, "/* 시연 데이터 — 지난 회의", DRAFT_FN + "/* 시연 데이터 — 지난 회의")
# 회의 기록 보기: 잡힌 회의에 [🖨 회의용 평가표 출력]
s = rep(s, "  if(done) B_.push(`<button class=\"btn ghost\" onclick=\"printMeeting('${m.id}')\">🖨 회의 결과 출력</button>`);\n",
        "  if(done) B_.push(`<button class=\"btn ghost\" onclick=\"printMeeting('${m.id}')\">🖨 회의 결과 출력</button>`);\n"
        "  if(m.status==='scheduled') B_.push(`<button class=\"btn ghost\" onclick=\"printMeetingDraft('${m.id}')\">🖨 회의용 평가표 출력</button>`);   /* V2: 회의 전에 출력 */\n")
# 위험성평가 리스트(관리소장): 잡힌 회의 카드에도
s = rep(s, ":`<div class=\"btn huge off\">${md(m.date)}에 시작할 수 있습니다</div>`}</div>`; });",
        ":`<div class=\"btn huge off\">${md(m.date)}에 시작할 수 있습니다</div>`}"
        "${mayRun(m)?`<button class=\"btn ghost\" style=\"margin-top:8px;width:100%\" onclick=\"printMeetingDraft('${m.id}')\">🖨 회의용 위험성평가표 출력</button>`:''}</div>`; });")
# 위험성평가: 끝난 회의의 평가표는 회의를 마친 때 내용 그대로 고정 (나중에 위험요인을 고쳐도 바뀌지 않음 · 개선 완료 여부만 계속 따라감)
s = rep(s, "function meetItems(m){ const rs=risksOf(m.bld); return (m.items||[]).map(id=>rs.find(r=>r.id===id)).filter(Boolean); }",
r"""/* V2 — 끝난 회의는 회의를 마친 때의 평가표 내용(m.snap)으로 보여 줌. 개선 완료 · 사진 등 이행 결과만 지금 값 */
const V2_SNAPF=['proc','place','type','hazard','current','l','s','score','measure','owner','due'];
function v2SnapOf(m){ const rs=risksOf(m.bld); return (m.items||[]).map(id=>rs.find(r=>r.id===id)).filter(Boolean)
  .map(r=>{ const o={id:r.id}; V2_SNAPF.forEach(k=>{ if(r[k]!==undefined) o[k]=r[k]; }); return o; }); }
function v2SnapAll(){ let n=0; Object.keys(S.blds).forEach(c=>(S.blds[c].rmeets||[]).forEach(m=>{ if(m.status==='done'&&!Array.isArray(m.snap)){ m.snap=v2SnapOf(m); n++; } })); if(n) saveS(); }
function meetItems(m){ const rs=risksOf(m.bld);
  if(m.status==='done'&&Array.isArray(m.snap)) return m.snap.map(sn=>Object.assign({},rs.find(x=>x.id===sn.id)||{},sn));
  return (m.items||[]).map(id=>rs.find(r=>r.id===id)).filter(Boolean); }""")
# 회의를 마치는 순간 고정
s = rep(s, "status:'done',heldAt:at,heldBy:curUser(),late:m.date<TODAYS?dayDiff(m.date,TODAYS):0});",
        "status:'done',heldAt:at,heldBy:curUser(),late:m.date<TODAYS?dayDiff(m.date,TODAYS):0}); m.snap=v2SnapOf(m);   /* V2: 평가표 고정 */")
# 이미 끝난 회의(시연 자료 포함)도 처음 열 때 한 번 고정
s = rep(s, "loadBuildings(); renderBldSel(); loadS(); applyRole();", "loadBuildings(); renderBldSel(); loadS(); v2SnapAll(); applyRole();")
# 안내 문구
s = rep(s, "'회의에서 검토할 위험요인'} <small class=\"hint\">· ${its.length}건</small>",
        "'회의에서 검토할 위험요인'} <small class=\"hint\">· ${its.length}건${done?' · 회의를 마친 때의 내용 그대로 (이후 위험요인을 고쳐도 바뀌지 않음)':''}</small>")
s = rep(s, "<h2>위험성평가표</h2><table><tr><th class=\"c\">공정</th>",
        "<h2>위험성평가표 <small style=\"font-weight:400\">· 회의를 마친 때의 내용</small></h2><table><tr><th class=\"c\">공정</th>")
# 경영방침은 2.0에서 뺐으므로(경영방침 화면 없음) 안전교육 리스트 · 나의 안전보건 · 경영책임자 현황 · 메뉴 숫자에서도 뺌
s = cut(s, "  /* 경영방침 서명 */\n", "  /* 예정된 집합 · 온라인 교육 */", "")                      # 안전교육 리스트: 경영방침 서명 현황
s = cut(s, "  if(!polRead) h+=", "  toConfirm.forEach(m=>{ h+=`<div class=\"sp-card\"><div class=\"k\">📋 위험성평가 결과 확인", "")   # 나의 안전보건: 서명하라는 카드
s = rep(s, "todo.length+(polRead?0:1)+live.length", "todo.length+live.length")                     # '확인할 일 n건'에서 경영방침 빼기
s = cut(s, "  if(polRead) past.push(", "  mts.filter(m=>m.status==='done'&&(m.att[key]", "")      # 지난 기록 목록
s = rep(s, "교육 · 경영방침 · 위험성평가</small></div>`", "교육 · 위험성평가</small></div>`")
s = rep(s, "    ['경영방침 열람',`${pct(rd.read,rd.total)}%`,`${rd.read} / ${rd.total}명 · v${ver}`],\n", "")   # 경영책임자 현황: 숫자 칸
s = rep(s, "  if(rd.total>rd.read) todo.push(['📄',`경영방침 v${ver} 미열람 종사자 ${rd.total-rd.read}명`,`goTab('policy')`]);\n", "")
s = rep(s, '<div class="kpis k5" id="ceoKpis">', '<div class="kpis" id="ceoKpis">')           # 5칸 → 4칸
# 경영방침 문구 정리 — 역할 안내 · 시연 초기화 설명
s = rep(s, "경영책임자 — 전 사업장 현황 확인 · 경영방침 제·개정 · 반기 점검 결재(본인 서명)", "경영책임자 — 전 사업장 현황 확인 · 반기 점검 결재(본인 서명)")
s = rep(s, "교육 행정 — 교육 계획 · 서류 관리 · 경영방침 게시 · 대표 결재 요청", "교육 행정 — 교육 계획 · 서류 관리 · 대표 결재 요청")
s = rep(s, "시연용 — 서명한 교육 공지 · 경영방침을 다시 '확인할 일'로 되돌립니다", "시연용 — 서명한 교육 공지를 다시 '확인할 일'로 되돌립니다")
s = rep(s, "'서명한 교육 공지 · 경영방침이 다시 \"확인할 일\"로 나옵니다.'", "'서명한 교육 공지가 다시 \"확인할 일\"로 나옵니다.'")
# 반기: 열 때마다 기준일 연도의 상반기
s = rep(s, "document.getElementById('halfSel').innerHTML=`<option value=\"${CUR.key}\">${CUR.label} (진행 중)</option><option value=\"${PREV.key}\">${PREV.label}</option>`;\n",
        "document.getElementById('halfSel').innerHTML=`<option value=\"${CUR.key}\">${CUR.label} (진행 중)</option><option value=\"${PREV.key}\">${PREV.label}</option>`;\n"
        "document.getElementById('halfSel').value=mkHalf(TODAY.getFullYear(),1).key;   /* V2: 항상 기준일 연도의 상반기부터 */\n")
# 나의 안전보건 (관리자 미리보기의 직원 고르기) · 안전교육 리스트 · 위험성평가 리스트
s = rep(s, "  const ws=workers(bldKey()); if(!ws.some(w=>w.key===myPickKey))", "  const ws=v2Ws(); if(!ws.some(w=>w.key===myPickKey))")
s = rep(s, "document.getElementById('myPick').innerHTML=workers(bldKey()).map(w=>`<option value=\"${w.key}\" ${w.key===key?'selected':''}>${esc(w.name)} · ${esc(w.pos)}</option>`)",
        "document.getElementById('myPick').innerHTML=v2Ws().map(w=>`<option value=\"${w.key}\" ${w.key===key?'selected':''}>${esc(w.name)} · ${esc(w.pos)}${V2_ALL?' · '+esc(bldName(w.bld)):''}</option>`)")
s = rep(s, "/* 교육 읽기 → 서명 (공지 · 경영방침 공용) */",
r"""/* V2 — [전체]면 건물마다 한 번씩 그려서 이어 붙임 (관리소장 등 소속 건물이 정해진 계정은 그대로) */
function v2EachBld(fn,boxId){ return function(){ if(!V2_ALL||myLinked()) return fn.apply(this,arguments);
  const box=document.getElementById(boxId); if(!box) return; let h='';
  try{ BUILDINGS.forEach(b=>{ V2_AT=b.code; fn(); h+=box.innerHTML; }); } finally{ V2_AT=null; } box.innerHTML=h; }; }
renderEduList=v2EachBld(renderEduList,'eduListBody'); renderRiskList=v2EachBld(renderRiskList,'riskListBody');
/* 교육 읽기 → 서명 (공지 · 경영방침 공용) */""")
# 계정 전환 → 메뉴를 새 주소로 다시 열기 (F5 없이 새 권한 · 새 화면)
s = rep(s, "    try{ if(window.top!==window){ window.top.location.reload(); return; } }catch(e){}",
        "    try{ if(window.top!==window){ window.top.location.replace('01_통합메뉴.html?t='+Date.now()); return; } }catch(e){}")
wr('04_안전보건.html', s)

# ===== 2) 01_통합메뉴: 안전보건 그룹 · 직책별 항목 · 빨간 숫자 · 내 할 일 먼저 열기 =====
v1 = rd('02_통합메뉴.html')
mp = _os.path.join(OUT, '01_통합메뉴.html')
m = _io.open(mp, encoding='utf-8').read().replace('\r\n', '\n')
# 메뉴 항목 — V1 안전보건 그룹을 그대로(링크만 04로), 건물관리 다음에
a = v1.index("  {ic:'🦺', label:'안전보건'"); b = v1.index("  {ic:'📨', label:'민원 · 공지'")
grp = v1[a:b].replace("link:'27_안전보건.html'", "link:'04_안전보건.html'")
grp = grp.replace("  {ic:'🦺', label:'안전보건', full:'안전보건관리(중대재해 대비)', tag:'new', kids:[",
                  "  {ic:'🦺', label:'안전보건', full:'안전보건관리(중대재해 대비)', tag:'new', perm:'안전보건', kids:[")
assert "perm:'안전보건'" in grp
# V2: 안전보건 메뉴는 6개 항목만
KEEP = ['plan', 'risk', 'my', 'edulist', 'risklist', 'ceo']   # 교육 공지는 교육 관리(plan)로 합침
grp = '\n'.join(l for l in grp.split('\n') if ('label:' not in l or "perm:'안전보건'" in l or any(f"tab:'{t}'" in l for t in KEEP)))
assert grp.count("link:'04_안전보건.html'") == len(KEEP), grp
# '나의 안전보건 리스트' → '나의 안전보건', 안전보건 메뉴 맨 위로
gl = grp.split('\n')
mine = [l for l in gl if "tab:'my'}" in l]
assert len(mine) == 1
gl.remove(mine[0])
gl.insert(1, mine[0].replace("label:'나의 안전보건 리스트', full:'나의 안전보건 리스트(", "label:'나의 안전보건', full:'나의 안전보건("))
# 교육 계획 · 실시는 교육 공지 · 서명 현황 바로 아래
plan = [l for l in gl if "tab:'plan'}" in l]; assert len(plan) == 1
gl.remove(plan[0]); _pl = plan[0].replace("label:'교육 계획 · 실시', full:'안전보건교육 계획 · 실시(서명)'", "label:'교육 관리', full:'교육 관리 (교육 공지 · 계획 · 실시 · 서명)'"); assert _pl != plan[0]
gl.insert([i for i, l in enumerate(gl) if "tab:'my'}" in l][0] + 1, _pl)
ceo = [l for l in gl if "tab:'ceo'}" in l]; assert len(ceo) == 1   # 경영책임자 현황은 안전보건 맨 위(대표만 보임)
gl.remove(ceo[0]); gl.insert(1, ceo[0])
grp = '\n'.join(gl)
assert "label:'나의 안전보건'," in grp
m = rep(m, "  {ic:'⚙️', label:'시스템 설정', tag:'keep', perm:'시스템 설정', kids:[", grp + "  {ic:'⚙️', label:'시스템 설정', tag:'keep', perm:'시스템 설정', kids:[")
# 직책별 안전보건 항목 · 빨간 숫자 계산 (V1 그대로)
sa = v1.index('const SAFETY_MENU='); sb = v1.index('function leafVisible(')
SAFETY = v1[sa:sb]
SAFETY = rep(SAFETY, "  '이사':['notice','ceo',", "  '이사':['notice',")
SAFETY = rep(SAFETY, "  '총무':['notice','ceo',", "  '총무':['notice',")
SAFETY = rep(SAFETY, "'대표':'notice'", "'대표':'ceo'")
SAFETY = rep(SAFETY, "':'notice'", "':'plan'", 3)
SAFETY = rep(SAFETY, "  const v=d.policy.versions[d.policy.versions.length-1].ver; if(!((b.reads||{})[v]||{})[s.worker]) edu++;\n", "")   # 경영방침은 2.0에 없음
   # 처음 여는 안전보건 화면: 교육 공지 → 교육 관리
NEWFN = ("/* 안전보건 항목은 직책별로(V1과 같음), 다른 메뉴는 그룹 권한대로 */\n"
         "function leafVisible(m,k){ if(v2Perm(m.perm||m.label)==='none') return false;\n"
         "  if(k.tab==='ceo'&&/안전보건\\.html$/.test(k.link||'')) return ROLE_NOW==='대표';   /* 경영책임자 현황은 대표만 */\n"
         "  if(/안전보건\\.html$/.test(k.link||'')){ const sm=SAFETY_MENU[ROLE_NOW]; return sm==='*'||(Array.isArray(sm)&&sm.includes(k.tab)); }\n"
         "  if(m.label==='안전보건') return ['관리자','대표','이사','총무'].includes(ROLE_NOW);   /* 예정 항목은 본사만 */\n"
         "  return true; }\n"
         "function openFirst(){\n"
         "  let want=false; try{ want=sessionStorage.getItem('bo_open_safety')==='1'; sessionStorage.removeItem('bo_open_safety'); }catch(e){}\n"
         "  const mi=MENU.findIndex(m=>m.label==='안전보건'), sm=SAFETY_MENU[ROLE_NOW];\n"
         "  const mine=Array.isArray(sm)&&sm.includes('my')&&myPending()>0;\n"
         "  if(mi>=0&&v2Perm('안전보건')!=='none'&&(want||mine||SAFETY_ONLY.includes(ROLE_NOW))){   /* 서명할 일이 있으면 나의 안전보건 리스트부터 */\n"
         "    const kids=MENU[mi].kids, home=myPending('my')>0?'my':(myPending('risk')>0&&Array.isArray(sm)&&sm.includes('risklist'))?'risklist':(SAFETY_HOME[ROLE_NOW]||'ceo');\n"
         "    let ki=kids.findIndex(k=>k.tab===home&&leafVisible(MENU[mi],k)); if(ki<0) ki=kids.findIndex(k=>k.link&&leafVisible(MENU[mi],k));\n"
         "    if(ki>=0){ document.querySelectorAll('.grp').forEach(g=>g.classList.toggle('open',+g.dataset.mi===mi)); openLeaf(mi,ki); return; } }\n"
         "  const el=document.querySelector('.leaf'); if(el){ openLeaf(+el.dataset.mi,+el.dataset.ki); return; }\n"
         "  const s=(()=>{ try{ return JSON.parse(localStorage.getItem('buildone_session')||'null'); }catch(e){ return null; } })();\n"
         "  const pane=document.getElementById('pane'); pane.className='pane';\n"
         "  pane.innerHTML=`<div class=\"placeholder\"><h2>열 수 있는 메뉴가 없습니다</h2><p class=\"d\">이 계정(${s?s.role:'-'})에는 권한이 있는 메뉴가 없습니다. 시스템관리자에게 권한을 요청하세요.</p></div>`; }\n\n")
m = cut(m, 'function leafVisible(m,k){ return v2Perm', 'function badge(tag)', SAFETY + NEWFN)
# 항목 옆 표시: 안전보건은 빨간 숫자(할 일), 다른 메뉴는 [조회]
m = rep(m, "${v2Perm(m.perm||m.label)==='view'?'<span class=\"badge\" title=\"조회만 할 수 있습니다\" style=\"background:#eef1f6;color:#5a6270\">조회</span>':''}",
        "${m.perm!=='안전보건'&&v2Perm(m.perm||m.label)==='view'?'<span class=\"badge\" title=\"조회만 할 수 있습니다\" style=\"background:#eef1f6;color:#5a6270\">조회</span>':''}"
        "${/안전보건\\.html$/.test(k.link||'')&&(k.tab==='my'||k.tab==='risklist')?pendBadge(k.tab==='my'?'my':'risk'):''}")
# 다른 탭 · 창에서 계정이 바뀌면 이 메뉴도 저절로 다시 열기
m = rep(m, '</body>', "<script>/* V2 — 계정이 바뀌면(다른 탭 포함) F5 없이 새 권한으로 다시 열기 */\n"
        "window.addEventListener('storage',e=>{ if(e.key==='buildone_session'){ if(!e.newValue){ location.replace('00_로그인.html'); return; } location.replace('01_통합메뉴.html?t='+Date.now()); } });\n</script>\n</body>")
assert '27_' not in m
open(mp, 'wb').write(m.replace('\n', '\r\n').encode('utf-8'))
print('안전보건 추가: 04_안전보건.html + 메뉴')
