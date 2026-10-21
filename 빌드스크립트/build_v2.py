# -*- coding: utf-8 -*-
"""빌드원시스템_V2 — 로그인 · 건물정보 등록 · 사용자/권한 3가지만 있는 버전 만들기
원본: 빌드원시스템\\프로토타입_HTML (V1 전달본) — V1은 건드리지 않음"""
import io, os, shutil

# 이 파일 위치 기준: 빌드원시스템_V2\빌드스크립트\build_v2.py → V2 = 빌드원시스템_V2, ROOT = 사업자 폴더
V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(V2)
SRC = os.path.join(ROOT, '빌드원시스템', '프로토타입_HTML')
OUT = os.path.join(V2, '프로토타입_HTML')
os.makedirs(OUT, exist_ok=True)


def rd(name):
    return io.open(os.path.join(SRC, name), encoding='utf-8').read().replace('\r\n', '\n')


def wr(name, s):
    open(os.path.join(OUT, name), 'wb').write(s.replace('\n', '\r\n').encode('utf-8'))


def rep(s, a, b, cnt=1):
    n = s.count(a)
    assert n == cnt, f'{n}x: {a[:70]}'
    return s.replace(a, b)


def cut(s, start, end, new):
    """start 문자열부터 end 문자열 직전까지를 new로 바꿈"""
    i = s.index(start); j = s.index(end, i)
    return s[:i] + new + s[j:]


# 공통: 로그인 게이트 (iframe 안이면 최상위 창을 로그인으로)
GATE = ("<script>/* V2 로그인 게이트 — 세션이 없으면 로그인 화면으로 */\n"
        "(function(){ try{ if(!localStorage.getItem('buildone_session')){ (window.top||window).location.replace('00_로그인.html'); } }catch(e){} })();\n"
        "</script>\n")
# 공통 권한 파일(common_perm.js) — 역할 · 그룹 · 기본 권한 · v2Perm · v2Deny
def _ver(name):   # 공통 파일이 바뀌면 주소가 달라져 브라우저가 새로 받음(옛 파일 기억 방지)
    return str(int(os.path.getmtime(os.path.join(OUT, name))))
COMMON = '<script src="common_perm.js?v=' + _ver('common_perm.js') + '"></script>\n'
PERM_JS = ''   # common_perm.js로 옮김
NOPERM = ''

HEADER = '<script src="common_header.js?v=' + _ver('common_header.js') + '"></script>\n'

# ===================== 00 로그인 =====================
s = rd('00_로그인.html')
s = rep(s, '<head>', '<head>\n' + COMMON, 1)
s = rep(s, "const HOME='02_통합메뉴.html';", "const HOME='01_통합메뉴.html';")
s = rep(s, "function computePerm(role){\n  try{", "function computePerm(role){\n  boEnsureRoles();   /* 역할 권한이 아직 없으면 기본값으로 (common_perm.js) */\n  try{")
s = rep(s, '<title>BuildOne — 로그인</title>', '<title>BuildOne 2.0 — 로그인</title>')
s = rep(s, '    <span class="wm">Build<i>One</i></span>\n  </div>\n  <p class="sub">집합건물 통합관리 시스템 · 로그인</p>',
        '    <span class="wm">Build<i>One</i></span><span class="v2">2.0</span>\n  </div>\n  <p class="sub">집합건물 통합관리 시스템 · 로그인</p>')
s = rep(s, '  .brand .wm i{font-style:normal;color:var(--accent);}',
        '  .brand .wm i{font-style:normal;color:var(--accent);}\n  .brand .v2{font-size:12px;font-weight:800;color:#fff;background:var(--accent);border-radius:6px;padding:2px 7px;margin-left:2px;align-self:center;}')
wr('00_로그인.html', s)

# ===================== 01 통합메뉴 =====================
s = rd('02_통합메뉴.html')
s = rep(s, '<head>', '<head>\n' + COMMON, 1)
s = rep(s, '<span class="tag">통합관리</span>', '<span class="tag">통합관리 2.0</span>')
MENU = """const MENU=[
  {ic:'🏢', label:'건물관리', full:'건물관리', tag:'keep', perm:'건물관리', kids:[
    {label:'건물정보 등록', full:'건물정보 등록', tag:'keep', link:'02_건물정보.html'},
  ]},
  {ic:'⚙️', label:'시스템 설정', tag:'keep', perm:'시스템 설정', kids:[
    {label:'사용자 · 권한', full:'사용자 · 권한(RBAC)', tag:'keep', link:'03_사용자권한.html'},
  ]},
];
"""
s = cut(s, 'const MENU=[', 'const TAG={', MENU)
V2MENU = ("/* V2 — 메뉴는 [사용자 · 권한]의 역할별 권한(로그인 때 buildone_perm에 저장: 그룹 → 없음/조회/편집)대로 보임 */\n"
          + PERM_JS +
          "function leafVisible(m,k){ return v2Perm(m.perm||m.label)!=='none'; }\n"
          "function openFirst(){ const el=document.querySelector('.leaf'); if(el){ openLeaf(+el.dataset.mi,+el.dataset.ki); return; }\n"
          "  const s=(()=>{ try{ return JSON.parse(localStorage.getItem('buildone_session')||'null'); }catch(e){ return null; } })();\n"
          "  const pane=document.getElementById('pane'); pane.className='pane';\n"
          "  pane.innerHTML=`<div class=\"placeholder\"><h2>열 수 있는 메뉴가 없습니다</h2><p class=\"d\">이 계정(${s?s.role:'-'})에는 권한이 있는 메뉴가 없습니다. 시스템관리자에게 권한을 요청하세요.</p></div>`; }\n\n")
s = cut(s, 'const SAFETY_MENU=', 'function badge(tag)', V2MENU)
s = rep(s, "${/안전보건\\.html$/.test(k.link||'')&&(k.tab==='my'||k.tab==='risklist')?pendBadge(k.tab==='my'?'my':'risk'):''}",
        "${v2Perm(m.perm||m.label)==='view'?'<span class=\"badge\" title=\"조회만 할 수 있습니다\" style=\"background:#eef1f6;color:#5a6270\">조회</span>':''}")
s = rep(s, "// 첫 화면: 대시보드 > 경영 현황(동작)\n", "// 첫 화면: 권한이 있는 첫 메뉴\n")
s = s.replace('<title>BuildOne — 통합 메뉴 (XPERP 벤치마킹 목업)</title>', '<title>BuildOne 2.0 — 통합 메뉴</title>')
# 화면(iframe)이 열려 있으면 위쪽 경로 줄 · 사용자 줄을 숨기고 화면 높이를 꽉 채움 — 경로 · 사용자 · 로그아웃은 각 화면 머리줄에(common_header.js)
s = rep(s, "  iframe{width:100%;height:calc(100vh - 45px);",
        "  body.framed .crumb,body.framed #userbar{display:none!important;} body.framed iframe{height:100vh;}\n  iframe{width:100%;height:calc(100vh - 45px);")
s = rep(s, "  const pane=document.getElementById('pane');\n  if(k.link){",
        "  const pane=document.getElementById('pane');\n  document.body.classList.toggle('framed',!!k.link);\n  if(k.link){")
assert 'SAFETY' not in s and 'myPending' not in s and '27_' not in s, 'V1 흔적 남음'
wr('01_통합메뉴.html', s)

# ===================== 02 건물정보 (V1 03_단지 → 건물정보 등록만) =====================
s = rd('03_단지.html')
s = rep(s, '<title>BuildOne — 단지관리 (XP PRO 벤치마킹)</title>', '<title>BuildOne 2.0 — 건물정보 등록</title>')
s = rep(s, '<head>', '<head>\n' + GATE + COMMON, 1)
s = rep(s, '  <div class="logo">BuildOne <small>단지관리 · 기본정보</small></div>', '  <div class="logo">BuildOne <small>건물관리 · 건물정보 등록</small></div>')
s = rep(s, """  <button data-t="info" class="on">① 단지(건물)정보</button>
  <button data-t="units">② 동호 생성</button>
  <button data-t="org">③ 입주자단체</button>
  <button data-t="meter">④ 세대별 검침대상·예외</button>""", """  <button data-t="info" class="on">건물정보</button>""")
# 다른 탭으로 이동 금지 (V2는 건물정보만)
s = rep(s, "function activateTabFromHash(){ const h=(location.hash||'').slice(1); const btn=document.querySelector(`.tabs button[data-t=\"${h}\"]`); if(btn)btn.click(); }",
        "function activateTabFromHash(){ const btn=document.querySelector('.tabs button[data-t=\"info\"]'); if(btn)btn.click(); }   /* V2: 건물정보만 */")
APPLY_DANJI = ("<script>/* V2 권한 적용 — 건물관리: 없음이면 차단, 조회면 보기 전용 */\n" + PERM_JS + NOPERM +
               "(function(){ const lv=v2Perm('건물관리'); if(lv==='none'){ v2Deny('건물정보 등록'); return; }\n"
               "  if(lv!=='view') return;\n"
               "  const st=document.createElement('style'); st.textContent='body.ro #info input,body.ro #info select,body.ro #info textarea{pointer-events:none;background:#f3f4f7!important;color:#555}'\n"
               "    +' body.ro #btnNewBld,body.ro #btnDelBld,body.ro #btnSaveInfo,body.ro #btnResetInfo,body.ro #btnResetAll{display:none!important}'\n"
               "    +' body.ro #bldSel{pointer-events:auto!important;background:#fafbfc!important;color:inherit}';\n"
               "  document.head.appendChild(st); document.body.classList.add('ro');\n"
               "  const b=document.createElement('div'); b.style.cssText='background:#fff7e0;border:1px solid #ead9a0;border-radius:8px;padding:10px 14px;margin:0 0 12px;font-size:13px';\n"
               "  b.innerHTML='🔒 <b>조회 권한</b> — 건물정보를 볼 수만 있습니다. 등록 · 수정 · 삭제는 편집 권한이 필요합니다.';\n"
               "  const pg=document.getElementById('info'); pg.insertBefore(b,pg.firstChild); })();\n</script>\n")
s = rep(s, '</body>', APPLY_DANJI + '</body>')
# 머리줄: 경로 · 사용자 · 로그아웃 (common_header.js) — 기존 머리줄 내용은 이 스크립트가 바꿔 씀
s = rep(s, '<head>\n' + GATE + COMMON, '<head>\n' + GATE + COMMON + HEADER)
s = rep(s, '<header>', '<header class="v2top">')
# 건물 선택 · 새 건물 등록 · 건물 삭제 → 건물 목록
s = cut(s, '    <div class="toolbar">\n      <strong style="font-size:13px">건물 선택</strong>', '    <div class="card">\n      <h3>',
        '    <select id="bldSel" style="display:none"></select>\n'
        '    <div class="card" id="bldListCard">\n'
        '      <h3>건물 목록 <span class="hint" id="bldCount" style="font-weight:400;margin:0 0 0 4px"></span></h3>\n'
        '      <div style="overflow-x:auto"><table class="bldlist"><thead><tr><th>No</th><th>건물명</th><th>지역 / 지점</th><th>건물코드</th><th>건물형태</th><th>소재지</th><th>대표자</th><th>관리소 연락처</th></tr></thead>\n'
        '        <tbody id="bldRows"></tbody></table></div>\n'
        '      <div class="hint" style="margin:8px 0 0">건물을 누르면 아래에 상세 정보가 나옵니다.</div>\n'
        '    </div>\n')
s = rep(s, "document.getElementById('btnNewBld').addEventListener('click',newBuilding);\n", '')
s = rep(s, "document.getElementById('btnDelBld').addEventListener('click',delBuilding);\n", '')
s = rep(s, "  .toolbar .spacer{flex:1;}",
        "  .toolbar .spacer{flex:1;}\n"
        "  .bldlist td,.bldlist th{text-align:left;white-space:normal;word-break:keep-all;} .bldlist td:first-child,.bldlist th:first-child{text-align:center;width:44px;}\n"
        "  .bldlist tbody tr{cursor:pointer;} .bldlist tbody tr:hover td{background:#f5f8ff;} .bldlist tbody tr.sel td{background:#eaf0ff;font-weight:600;}")
# 목록 그리기 — 로그인 계정의 접근 건물만 (관리자 · 전체 건물 계정은 모두)
s = rep(s, "function renderBldSel(){ document.getElementById('bldSel').innerHTML=BUILDINGS.map((b,i)=>`<option value=\"${i}\" ${i===curBld?'selected':''}>${bldLabel(b)}</option>`).join(''); }",
        "function renderBldSel(){ document.getElementById('bldSel').innerHTML=BUILDINGS.map((b,i)=>`<option value=\"${i}\" ${i===curBld?'selected':''}>${bldLabel(b)}</option>`).join(''); renderBldList(); }\n"
        "const bEsc=t=>String(t==null?'':t).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));\n"
        "function bldVisible(){ let s=null; try{ s=JSON.parse(localStorage.getItem('buildone_session')||'null'); }catch(e){}\n"
        "  const all=BUILDINGS.map((b,i)=>i); if(!s||s.role==='관리자'||!Array.isArray(s.buildings)) return all;\n"
        "  return all.filter(i=>s.buildings.includes(BUILDINGS[i].code)); }\n"
        "function renderBldList(){ const idx=bldVisible();\n"
        "  if(idx.length&&!idx.includes(curBld)){ curBld=idx[0]; loadBldToForm(); loadBldData(); }\n"
        "  document.getElementById('bldCount').textContent='· '+idx.length+'개';\n"
        "  document.getElementById('bldRows').innerHTML=idx.length?idx.map((i,n)=>{ const b=BUILDINGS[i];\n"
        "    return `<tr class=\"${i===curBld?'sel':''}\" onclick=\"switchBld(${i})\"><td>${n+1}</td><td><b>${bEsc(b.name)}</b></td><td>${bEsc(b.region||'-')}</td><td>${bEsc(b.code)}</td><td>${bEsc(b.type||'-')}</td><td>${bEsc(b.addr||'-')}</td><td>${bEsc(b.ceo||'-')}</td><td>${bEsc(b.tel||'-')}</td></tr>`; }).join('')\n"
        "    :'<tr><td colspan=\"8\" style=\"text-align:center;color:#6b727c;padding:18px\">접근할 수 있는 건물이 없습니다 — [사용자 · 권한] > 접근 건물에서 지정합니다</td></tr>';\n"
        "  document.querySelectorAll('#info > .card:not(#bldListCard)').forEach(c=>c.style.display=idx.length?'':'none'); }")
s = rep(s, "curBld=i; localStorage.setItem('buildone_current_building', i); loadBldToForm(); loadBldData(); renderAll(); }",
        "curBld=i; localStorage.setItem('buildone_current_building', i); loadBldToForm(); loadBldData(); renderAll(); renderBldList(); }")
s = rep(s, "if(!isNaN(i) && i>=0 && i<BUILDINGS.length && i!==curBld){ curBld=i; renderBldSel();", "if(!isNaN(i) && i>=0 && i<BUILDINGS.length && i!==curBld){ curBld=i; renderBldSel();")
# 화면에 보이는 문구: 단지 → 건물
for a, b in [
    ('<h3>단지(건물) 기본정보 <span', '<h3>건물 기본정보 <span'),
    ('<label>단지명(건물명) <span class="req">', '<label>건물명 <span class="req">'),
    ('<label>단지코드(5자리, 수정불가)</label>', '<label>건물코드(5자리, 수정불가)</label>'),
    ('<label>단지형태</label>', '<label>건물형태</label>'),
    ('id="btnSaveInfo" disabled>단지정보 저장</button>', 'id="btnSaveInfo" disabled>건물정보 저장</button>'),
    ("nameErr?'단지명은 필수입니다':''", "nameErr?'건물명은 필수입니다':''"),
    ("toast('단지정보 저장 완료 (통합메뉴 목록 반영)','ok');", "toast('건물정보 저장 완료 (통합메뉴 목록 반영)','ok');"),
]:
    s = rep(s, a, b)
exec(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v2_step_popup.py'), encoding='utf-8').read())   # 건물 기본정보 팝업 · 새 건물 · 삭제
wr('02_건물정보.html', s)

# ===================== 03 사용자권한 =====================
s = rd('26_사용자권한.html')
s = rep(s, '<title>BuildOne — 사용자 · 권한 관리</title>', '<title>BuildOne 2.0 — 사용자 · 권한</title>')
s = rep(s, '<head>', '<head>\n' + GATE + COMMON, 1)
s = cut(s, "const ROLES=['관리자'", "function rolePerm(o)",
        "const ROLES=BO_ROLES;\n"
        "// V2 — 통합메뉴(01)에 있는 메뉴 그룹만. 역할 · 그룹 · 기본 권한은 common_perm.js 한 곳에서 관리\n"
        "const GROUPS=BO_GROUPS;\nconst LEVELS=BO_LEVELS;\nconst LEVEL_LABEL={none:'없음', view:'조회', edit:'편집'};\nconst DEFAULT_ROLES=BO_DEFAULT_ROLES;\n")
# 계정 삭제 → 사용 안 함 (기록 주인이 사라지지 않게)
s = rep(s, """      <button class="btn sm danger" onclick="delUser('${u.id}')">삭제</button>""",
        """      <button class="btn sm ${u.active!==false?'danger':'gray'}" onclick="delUser('${u.id}')">${u.active!==false?'사용 안 함':'다시 사용'}</button>""")
s = rep(s, """window.delUser=function(id){
  if(!confirm(id+' 사용자를 삭제할까요?')) return;
  users=users.filter(x=>x.id!==id); jset(LS.users,users); renderUsers();
};""", """window.delUser=function(id){   /* V2: 계정은 지우지 않고 '사용 안 함'으로 — 그 사람이 남긴 기록의 주인이 사라지지 않게 */
  const u=users.find(x=>x.id===id); if(!u) return;
  if(sess&&sess.id===id){ alert('본인 계정은 사용 안 함으로 바꿀 수 없습니다.'); return; }
  const off=u.active!==false;
  if(!confirm(off?`${u.name}(${id}) 계정을 사용 안 함으로 바꿀까요?\\n로그인만 막히고 계정 기록은 그대로 남습니다.`:`${u.name}(${id}) 계정을 다시 사용할까요?`)) return;
  u.active=!off; jset(LS.users,users); renderUsers();
};""")
# 본인 역할 변경 금지 · 관리자 역할은 관리자만
s = rep(s, """  if(!editId && users.some(u=>u.id===id)){ alert('이미 존재하는 아이디입니다.'); return; }""",
        """  if(!editId && users.some(u=>u.id===id)){ alert('이미 존재하는 아이디입니다.'); return; }
  const isAdmin=sess&&sess.role==='관리자';
  if(role==='관리자'&&!isAdmin){ alert('관리자 역할은 시스템관리자만 줄 수 있습니다.'); return; }
  if(editId&&sess&&editId===sess.id){ const me=users.find(x=>x.id===editId);
    if(me&&me.role!==role){ alert('본인의 역할은 바꿀 수 없습니다.'); return; }
    if(!active){ alert('본인 계정은 사용 안 함으로 바꿀 수 없습니다.'); return; } }""")
# 권한 적용: 정해지지 않았으면 거부 (V1은 편집 허용이었음)
s = rep(s, """  const lvl=(jget('buildone_perm',{})['시스템 설정'])||'edit';   // 미설정/직접열람 시 편집 허용
  if(lvl!=='view') return;""", """  const lvl=v2Perm('시스템 설정');   // V2: 관리자는 편집, 정해지지 않았으면 없음(거부)
  if(lvl==='none'){ v2Deny('사용자 · 권한'); return; }
  if(lvl!=='view') return;""")
s = rep(s, "// ================= #2 권한 적용 — '시스템 설정'이 조회면 이 화면 읽기전용 =================",
        "// ================= 권한 적용 — '시스템 설정'이 없음이면 차단, 조회면 읽기전용 =================\n" + PERM_JS + NOPERM)
s = rep(s, "alert('역할별 권한을 저장했습니다. (로그인한 사용자는 다음 로그인부터 적용)');",
        "if(sess&&roles[sess.role]) localStorage.setItem('buildone_perm',JSON.stringify(roles[sess.role]));   /* 내 권한은 바로 반영 */\n  alert('역할별 권한을 저장했습니다. (다른 사용자는 다음 로그인부터 적용)');")
s = rep(s, '<head>\n' + GATE + COMMON, '<head>\n' + GATE + COMMON + HEADER)
s = rep(s, '</style>', '  .actions .btn{white-space:nowrap;}   /* V2: [사용 안 함] 한 줄로 */\n</style>', 1)
s = rep(s, "'건물 목록은 <b>단지관리</b>에서 등록한 건물을 사용합니다.", "'건물 목록은 <b>건물관리 > 건물정보 등록</b>에서 등록한 건물을 사용합니다.")
exec(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v2_step_users.py'), encoding='utf-8').read())   # ①사용자만 · 접근 건물 ▾ 고르기
wr('03_사용자권한.html', s)

# ===================== 아이콘 =====================
shutil.copytree(os.path.join(SRC, '아이콘'), os.path.join(OUT, '아이콘'), dirs_exist_ok=True)
exec(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v2_step_safety.py'), encoding='utf-8').read())   # 안전보건(V1 그대로)
exec(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v2_step_dash.py'), encoding='utf-8').read())   # 대시보드 · 오늘의 할 일
exec(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v2_step_fresh.py'), encoding='utf-8').read())   # 항상 새 화면
print('V2 built:', sorted(os.listdir(OUT)))
