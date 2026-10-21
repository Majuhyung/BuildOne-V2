# -*- coding: utf-8 -*-
# build_v2.py 안에서 exec — 03_사용자권한: ①사용자 탭만, 접근 건물은 ▾ 눌러 모든 건물에서 고르기(사용자 추가 · 사용자 목록)
# (변수 s, 함수 rep 를 build_v2.py에서 그대로 씀)

# ---- 1) ②역할 · 권한, ③접근 건물 탭 숨김 (코드는 남겨 두고 화면에서만 뺌 — 권한은 common_perm.js 기본값) ----
s = rep(s, '<div class="tabs">\n  <button data-t="users" class="on">① 사용자</button>',
        '<div class="tabs" style="display:none">\n  <button data-t="users" class="on">① 사용자</button>')
s = rep(s, '<section class="page" id="p-roles">', '<section class="page" id="p-roles" style="display:none!important">')
s = rep(s, '<section class="page" id="p-bldgs">', '<section class="page" id="p-bldgs" style="display:none!important">')
s = rep(s, '<p>로그인 계정 · 역할별 메뉴 권한 · 건물별 접근을 관리합니다.', '<p>로그인 계정과 계정별 역할 · 접근 건물을 관리합니다.')
s = rep(s, '사용자를 등록하고 <b>역할</b>과 <b>접근 건물</b>을 지정합니다. 역할별 메뉴 권한은 <b>②역할·권한</b> 탭에서 정의합니다.',
        '사용자를 등록하고 <b>역할</b>과 <b>접근 건물</b>을 지정합니다. 접근 건물은 <b>▾</b>를 눌러 건물을 고릅니다. (사용자 목록에서도 바로 바꿀 수 있습니다)')
s = rep(s, "※ '전체 건물' 외 특정 건물 지정은 <b>③접근 건물</b> 탭에서 · 신규 계정은",
        "※ <b>전체 건물</b>은 앞으로 추가될 건물까지 포함합니다 · 신규 계정은")

# ---- 2) 사용자 추가: 접근 건물 고르기 ----
s = rep(s, '<div class="fld"><label>접근 건물</label><select id="f_bld"><option value="all">전체 건물</option></select></div>',
        '<div class="fld"><label>접근 건물</label><div id="f_bldPick"></div></div>')
s = rep(s, "  const bldSel=document.getElementById('f_bld').value;", "  const bldSel=formBlds;")
s = rep(s, "  if(!id||!name||!pw){ alert('아이디·이름·비밀번호는 필수입니다.'); return; }",
        "  if(!id||!name||!pw){ alert('아이디·이름·비밀번호는 필수입니다.'); return; }\n"
        "  if(bldSel!=='all'&&!bldSel.length){ alert('접근 건물을 하나 이상 고르세요.'); return; }")
s = rep(s, "    if(bldSel==='all') u.buildings='all'; else if(u.buildings==='all') u.buildings=[]; // custom은 ③탭에서 지정",
        "    u.buildings=bldSel==='all'?'all':bldSel.slice();")
s = rep(s, "    users.push({id,name,pw,role,active,buildings: bldSel==='all'?'all':[], mustChange:true});",
        "    users.push({id,name,pw,role,active,buildings: bldSel==='all'?'all':bldSel.slice(), mustChange:true});")
s = rep(s, "  document.getElementById('f_bld').value=(u.buildings==='all')?'all':'custom';",
        "  setFormBlds(u.buildings==='all'?'all':(Array.isArray(u.buildings)?u.buildings.slice():[]));")
s = rep(s, "  document.getElementById('f_bld').value='all'; document.getElementById('f_active').value='1';",
        "  setFormBlds('all'); document.getElementById('f_active').value='1';")

# ---- 3) 사용자 목록: 접근 건물 칸도 ▾ 로 ----
s = rep(s, "    <td>${bldLabel(u.buildings)}</td>", "    <td>${bpickBtn('u:'+u.id,u.buildings)}</td>")

# ---- 4) 모양 ----
s = rep(s, '  .actions{display:flex;gap:6px;}',
        '  .actions{display:flex;gap:6px;}\n'
        '  .bpick-btn{display:inline-flex;align-items:center;justify-content:space-between;gap:10px;min-width:180px;max-width:280px;border:1px solid var(--line);background:#fff;border-radius:7px;padding:8px 10px;font-size:13px;font-family:inherit;color:inherit;cursor:pointer;text-align:left;}\n'
        '  td .bpick-btn{min-width:150px;padding:5px 9px;font-size:12px;} .bpick-btn:hover{border-color:var(--accent);} .bpick-btn .t{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;} .bpick-btn .a{color:var(--sub);font-size:11px;}\n'
        '  #bpPop{position:fixed;z-index:200;background:#fff;border:1px solid var(--line);border-radius:10px;box-shadow:0 10px 30px rgba(20,30,50,.18);padding:10px 12px;min-width:240px;max-height:320px;overflow:auto;display:none;}\n'
        '  #bpPop label{display:flex;align-items:center;gap:8px;padding:6px 4px;font-size:13px;cursor:pointer;border-radius:6px;} #bpPop label:hover{background:#f4f7ff;} #bpPop small{color:var(--sub);margin-left:auto;}\n'
        '  #bpPop .bp-all{font-weight:700;border-bottom:1px solid var(--line);border-radius:0;margin-bottom:4px;padding-bottom:8px;} #bpPop .bp-f{display:flex;justify-content:flex-end;gap:6px;margin-top:8px;}')

# ---- 5) 동작 ----
PICK_JS = r'''<script>/* V2 — 접근 건물 고르기 (▾ 누르면 모든 건물) */
const bpEsc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function bldSummary(v){ if(v==='all') return '전체 건물'; const a=Array.isArray(v)?v:[]; if(!a.length) return '선택 안 함';
  const n=a.map(c=>{ const f=bldgs.find(x=>x.code===c); return f?f.name:c; }); return n.length<=2?n.join(', '):n[0]+' 외 '+(n.length-1)+'곳'; }
function bpickBtn(key,v){ return `<button type="button" class="bpick-btn" data-k="${bpEsc(key)}" title="${bpEsc(v==='all'?'전체 건물':(Array.isArray(v)?v.map(c=>{const f=bldgs.find(x=>x.code===c);return f?f.name:c;}).join(', '):''))}"><span class="t">${bpEsc(bldSummary(v))}</span><span class="a">▾</span></button>`; }
let formBlds='all';
function setFormBlds(v){ formBlds=v; document.getElementById('f_bldPick').innerHTML=bpickBtn('form',v); }
const pop=document.createElement('div'); pop.id='bpPop'; document.body.appendChild(pop);
let popKey=null;
function closePop(){ pop.style.display='none'; popKey=null; }
function openPop(btn){
  bldgs=loadBldgs();
  const key=btn.dataset.k, cur=key==='form'?formBlds:((users.find(u=>'u:'+u.id===key)||{}).buildings);
  const all=cur==='all', set=Array.isArray(cur)?cur:[];
  pop.innerHTML=`<label class="bp-all"><input type="checkbox" data-all ${all?'checked':''}> 전체 건물 <small>앞으로 추가될 건물 포함</small></label>`
    +bldgs.map(b=>`<label><input type="checkbox" data-code="${bpEsc(b.code)}" ${all||set.includes(b.code)?'checked':''} ${all?'disabled':''}> ${bpEsc(b.name)} <small>${bpEsc(b.code)}</small></label>`).join('')
    +`<div class="bp-f"><button type="button" class="btn gray" data-x>닫기</button><button type="button" class="btn" data-ok>적용</button></div>`;
  const r=btn.getBoundingClientRect(); pop.style.display='block';
  const z=parseFloat(getComputedStyle(document.body).zoom)||1;   /* 화면 확대(1.15배) 보정 */
  let left=r.left/z, top=(r.bottom+4)/z; const pw=pop.offsetWidth, ph=pop.offsetHeight, vw=innerWidth/z, vh=innerHeight/z;
  if(left+pw>vw-8) left=Math.max(8,vw-pw-8); if(top+ph>vh-8) top=Math.max(8,r.top/z-ph-4);
  pop.style.left=left+'px'; pop.style.top=top+'px'; popKey=key;
  pop.querySelector('[data-all]').addEventListener('change',e=>{ pop.querySelectorAll('[data-code]').forEach(x=>{ x.disabled=e.target.checked; if(e.target.checked) x.checked=true; }); });
  pop.querySelector('[data-x]').addEventListener('click',closePop);
  pop.querySelector('[data-ok]').addEventListener('click',()=>{
    const v=pop.querySelector('[data-all]').checked?'all':[...pop.querySelectorAll('[data-code]:checked')].map(x=>x.dataset.code);
    if(v!=='all'&&!v.length){ alert('접근 건물을 하나 이상 고르세요.'); return; }
    if(key==='form'){ setFormBlds(v); }
    else { const u=users.find(x=>'u:'+x.id===key); if(u){ u.buildings=v; jset(LS.users,users);
      if(sess&&sess.id===u.id){ sess.buildings=v; localStorage.setItem('buildone_session',JSON.stringify(sess)); }   /* 내 계정이면 바로 반영 */
      renderUsers(); } }
    closePop(); });
}
document.addEventListener('click',e=>{ const b=e.target.closest('.bpick-btn'); if(b){ e.stopPropagation(); if(popKey===b.dataset.k){ closePop(); return; } openPop(b); return; }
  if(popKey&&!e.target.closest('#bpPop')) closePop(); });
document.addEventListener('keydown',e=>{ if(e.key==='Escape') closePop(); });
window.addEventListener('scroll',closePop,true);
setFormBlds('all'); renderUsers();
</script>
'''
s = rep(s, '</body>', PICK_JS + '</body>')

# ---- 6) 처음 목록 그리기는 고르기 준비(PICK_JS) 뒤로 ----
s = rep(s, "fillRoleSelect(); renderUsers();", "fillRoleSelect();   /* 사용자 목록은 접근 건물 고르기 준비 뒤(아래 스크립트)에서 그림 */")

# ---- 7) 사용자 목록: 이름 · 역할 · 상태 칸은 한 줄로 ----
s = rep(s, '  .actions{display:flex;gap:6px;}\n  .bpick-btn{',
        '  .actions{display:flex;gap:6px;}\n  #uRows td:nth-child(2),#uRows td:nth-child(3),#uRows td:nth-child(5){white-space:nowrap;}\n  .bpick-btn{')
