# -*- coding: utf-8 -*-
# build_v2.py 안에서 exec — 02_건물정보: 건물 기본정보를 팝업으로, 수납 우선순위 숨김, 새 건물 등록 · 행 삭제 버튼
# (변수 s, 함수 rep / cut 을 build_v2.py에서 그대로 씀)

# ---- 1) 건물 기본정보 카드 + 수납 우선순위 카드 → 팝업(dialog) ----
i = s.index('    <div class="card">\n      <h3>건물 기본정보')
j = s.index('  </section>\n\n  <!-- ② 동호 생성 -->')
block = s[i:j]
f0 = block.index('      <div class="form">')
f1 = block.index('    <div class="card">\n      <h3>수납 우선순위')
form = block[f0:f1]
assert form.endswith('    </div>\n'), 'form 끝 모양이 다름'
form = form[:-len('    </div>\n')]          # 기본정보 카드의 닫는 </div> 제거 → 폼만
DLG = ('    <dialog id="bldDlg">\n'
       '      <div class="dlg-h"><span id="bldDlgTitle">건물 기본정보</span> <span class="dirty-badge" id="dirty">● 저장되지 않은 변경</span></div>\n'
       '      <div class="dlg-b">\n'
       + form +
       '        <!-- 수납 우선순위: V2 화면에서는 뺌 — 값은 그대로 보관(수납 모듈 기본값) -->\n'
       '        <div style="display:none"><select id="f_lateType"><option value="normal">일반 연체료</option><option value="daily">연체료 일할</option></select><select id="f_alloc"></select><span id="saveHint"></span></div>\n'
       '      </div>\n'
       '      <div class="dlg-f"><button class="btn gray sm" id="btnResetInfo" disabled>변경 취소</button><span style="flex:1"></span>'
       '<button class="btn gray" id="btnCloseBld">닫기</button><button class="btn" id="btnSaveInfo" disabled>저장</button></div>\n'
       '    </dialog>\n')
s = s[:i] + DLG + s[j:]

# ---- 2) 팝업 모양 ----
s = rep(s, '  dialog#editDlg{border:0;',
        '  dialog#bldDlg{border:0;border-radius:12px;padding:0;width:760px;max-width:80vw;max-height:78vh;box-shadow:0 12px 44px rgba(0,0,0,.25);}\n'
        '  dialog#bldDlg::backdrop{background:rgba(20,25,35,.45);} dialog#bldDlg .dlg-b{max-height:calc(78vh - 120px);overflow:auto;}\n'
        '  #bldListCard h3{display:flex;align-items:center;gap:6px;} .bldlist td.bldDelTd{width:60px;text-align:center;}\n'
        '  dialog#editDlg{border:0;')

# ---- 3) 건물 목록: 오른쪽 끝 [새 건물 등록], 행 끝 [삭제], 누르면 팝업 ----
s = rep(s, '      <h3>건물 목록 <span class="hint" id="bldCount" style="font-weight:400;margin:0 0 0 4px"></span></h3>',
        '      <h3>건물 목록 <span class="hint" id="bldCount" style="font-weight:400;margin:0 0 0 4px"></span><span style="flex:1"></span>'
        '<button class="btn sm" id="btnNewBld">+ 새 건물 등록</button></h3>')
s = rep(s, '<th>대표자</th><th>관리소 연락처</th></tr></thead>', '<th>대표자</th><th>관리소 연락처</th><th></th></tr></thead>')
s = rep(s, '건물을 누르면 아래에 상세 정보가 나옵니다.', '건물을 누르면 상세 정보가 팝업으로 열립니다.')
s = rep(s, 'onclick="switchBld(${i})"', 'onclick="openBld(${i})"')
s = rep(s, "<td>${bEsc(b.tel||'-')}</td></tr>`",
        "<td>${bEsc(b.tel||'-')}</td><td class=\"bldDelTd\"><button class=\"btn danger sm bldDel\" onclick=\"event.stopPropagation();delBldAt(${i})\">삭제</button></td></tr>`")
s = rep(s, '<tr><td colspan="8" style="text-align:center;', '<tr><td colspan="9" style="text-align:center;')

# 조회 권한: 새 건물 · 삭제 · 저장 숨김 (팝업 입력칸은 기존 #info 규칙으로 잠김)
s = rep(s, "body.ro #btnNewBld,body.ro #btnDelBld,", "body.ro #btnNewBld,body.ro .bldDel,body.ro #btnDelBld,")

# ---- 4) 팝업 동작 ----
POPUP_JS = r'''<script>/* V2 — 건물 기본정보 팝업 · 새 건물 등록 · 삭제 */
let dlgNew=null;   /* 새 건물 등록 중이면 그 건물 값 (저장할 때만 목록에 추가) */
const bldDlg=document.getElementById('bldDlg');
function fillForm(b){ document.getElementById('f_lateType').value=b.lateType||'normal'; fillAlloc();
  BFIELDS.forEach(([id,key])=>{ if(id==='f_lateType')return; const el=document.getElementById(id); if(el) el.value=(b[key]!==undefined?b[key]:''); });
  validateInfo(); infoSnapshot=snapshotInfo(); setDirty(false); }
window.openBld=function(i){ dlgNew=null; curBld=i; localStorage.setItem('buildone_current_building',i);
  loadBldToForm(); loadBldData(); renderBldList();
  document.getElementById('bldDlgTitle').textContent='건물 기본정보 — '+bldLabel(BUILDINGS[i]); bldDlg.showModal(); };
function openNewBld(){ dlgNew={code:'N'+String(Date.now()).slice(-4),name:'',region:'',type:'빌딩',ec:'',addr:'',biz:'',ceo:'',tel:'',acct:'일반(집합건물)',lateType:'normal',alloc:'principal'};
  fillForm(dlgNew); document.getElementById('m_name').textContent='';
  document.getElementById('bldDlgTitle').textContent='새 건물 등록'; bldDlg.showModal(); document.getElementById('f_name').focus(); }
function closeBldDlg(){ if(infoDirty&&!confirm('저장하지 않은 변경이 있습니다. 닫을까요?')) return;
  dlgNew=null; loadBldToForm(); bldDlg.close(); }
/* 새 건물을 만든 사람이 건물 지정 계정이면 그 건물에 접근할 수 있게 */
function grantNewBld(code){ try{ const s=JSON.parse(localStorage.getItem('buildone_session')||'null'); if(!s||!Array.isArray(s.buildings)) return;
  s.buildings.push(code); localStorage.setItem('buildone_session',JSON.stringify(s));
  const us=JSON.parse(localStorage.getItem('buildone_users')||'[]'), u=us.find(x=>x.id===s.id); if(u&&Array.isArray(u.buildings)){ u.buildings.push(code); localStorage.setItem('buildone_users',JSON.stringify(us)); } }catch(e){} }
function saveBldDlg(){ if(!validateInfo()){ toast('입력값을 확인하세요','bad'); return; }
  const isNew=!!dlgNew;
  if(isNew){ BUILDINGS.push(Object.assign({},dlgNew)); curBld=BUILDINGS.length-1; localStorage.setItem('buildone_current_building',curBld); grantNewBld(dlgNew.code); }
  saveInfo(); dlgNew=null; bldDlg.close(); if(isNew){ loadBldData(); toast('새 건물을 등록했습니다','ok'); } }
window.delBldAt=function(i){ const b=BUILDINGS[i]; if(!b) return;
  if(BUILDINGS.length<=1){ toast('최소 1개 건물은 있어야 합니다','bad'); return; }
  if(!confirm(bldLabel(b)+' 건물을 삭제할까요?\n이 건물의 동호 · 단체 · 검침환경 데이터도 함께 삭제됩니다.')) return;
  try{ const all=readAllData(); delete all[b.code]; localStorage.setItem(LS_DATA, JSON.stringify(all)); }catch(e){}
  BUILDINGS.splice(i,1); if(curBld>=BUILDINGS.length||curBld===i) curBld=0; else if(curBld>i) curBld--;
  localStorage.setItem('buildone_current_building',curBld); persistBuildings(); renderBldSel(); loadBldToForm(); loadBldData(); renderAll(); toast('건물을 삭제했습니다','warn'); };
document.getElementById('btnNewBld').addEventListener('click',openNewBld);
document.getElementById('btnCloseBld').addEventListener('click',closeBldDlg);
bldDlg.addEventListener('cancel',e=>{ e.preventDefault(); closeBldDlg(); });
/* 저장 버튼은 팝업 저장으로 바꿈 (기존 saveInfo 연결 대신) */
const sb=document.getElementById('btnSaveInfo'), sb2=sb.cloneNode(true); sb.parentNode.replaceChild(sb2,sb); sb2.addEventListener('click',saveBldDlg);
</script>
'''
s = rep(s, '</body>', POPUP_JS + '</body>')

# ---- 5) 목록 칸 줄바꿈: 짧은 칸은 한 줄, 소재지 · 대표자만 줄바꿈 ----
s = rep(s, '  #bldListCard h3{display:flex;align-items:center;gap:6px;}',
        '  #bldListCard h3{display:flex;align-items:center;gap:6px;}\n'
        '  .bldlist th,.bldlist td{white-space:nowrap!important;} .bldlist td:nth-child(6),.bldlist td:nth-child(7){white-space:normal!important;min-width:90px;} .bldlist th,.bldlist td{padding:8px 7px!important;}')

# ---- 6) 사업자번호 · 연락처: 글자 수 제한 때문에 입력이 막혀 [변경 취소]가 안 켜지던 문제 ----
#      maxlength 제거(서식 함수가 10/11자리로 자름) · 하이픈 넣어도 커서 자리 유지 · 변경 여부는 처음 값과 비교
s = rep(s, ' maxlength="12" placeholder="000-00-00000"', ' placeholder="000-00-00000"')
s = rep(s, ' maxlength="13" inputmode="numeric" placeholder="02-000-0000"', ' inputmode="numeric" placeholder="02-000-0000"')
s = rep(s, "INFO_IDS.forEach(id=>{ const el=document.getElementById(id); el.addEventListener('input',()=>{ if(id==='f_biz')el.value=formatBiz(el.value); if(id==='f_tel')el.value=formatPhone(el.value); validateInfo(); setDirty(true); }); el.addEventListener('change',()=>setDirty(true)); });",
        "/* 숫자 칸 서식(하이픈)을 넣어도 커서 자리 유지 */\n"
        "function fmtKeepCaret(el,fmt){ const pos=el.selectionStart||0, before=el.value.slice(0,pos).replace(/[^0-9]/g,'').length; el.value=fmt(el.value);\n"
        "  let n=0,i=0; while(i<el.value.length&&n<before){ if(/[0-9]/.test(el.value[i]))n++; i++; } try{ el.setSelectionRange(i,i); }catch(e){} }\n"
        "/* 변경 여부 = 처음(또는 마지막 저장) 값과 다른지 — 되돌려 쓰면 '변경 없음'으로 */\n"
        "function refreshDirty(){ setDirty(INFO_IDS.some(k=>document.getElementById(k).value!==infoSnapshot[k])); }\n"
        "INFO_IDS.forEach(id=>{ const el=document.getElementById(id); el.addEventListener('input',()=>{ if(id==='f_biz')fmtKeepCaret(el,formatBiz); if(id==='f_tel')fmtKeepCaret(el,formatPhone); validateInfo(); refreshDirty(); }); el.addEventListener('change',refreshDirty); });")

# ---- 7) 건물 · 기준일 줄: 건물 선택은 목록으로 대신하므로 숨김 (안전보건 화면은 건물 선택 그대로) ----
s = rep(s, '  #bldListCard h3{display:flex;', '  .bo-ctxbar label,.bo-ctxbar .bo-bld{display:none!important;}\n  #bldListCard h3{display:flex;')
