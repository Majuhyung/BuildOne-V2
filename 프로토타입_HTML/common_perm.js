/* BuildOne 2.0 공통 — 역할 · 메뉴 그룹 · 기본 권한
   로그인(00) · 통합메뉴(01) · 건물정보(02) · 사용자권한(03) · 안전보건(04)이 함께 씁니다. 메뉴 그룹을 늘리면 여기와 01의 MENU를 같이 고칩니다. */
var BO_ROLES=['관리자','대표','이사','총무','관리소장','시설관리주임','경리','미화원','경비','건물주'];
var BO_GROUPS=['건물관리','안전보건','시스템 설정'];
var BO_LEVELS=['none','view','edit'];
function boRolePerm(o){ var r={}; BO_GROUPS.forEach(function(g){ r[g]=(o.edit||[]).indexOf(g)>=0?'edit':(o.view||[]).indexOf(g)>=0?'view':'none'; }); return r; }
var BO_DEFAULT_ROLES={
  '관리자':      boRolePerm({edit:BO_GROUPS}),                       // 시스템관리자 — 항상 전체 편집
  '대표':        boRolePerm({edit:['안전보건'], view:['건물관리']}),
  '이사':        boRolePerm({edit:['안전보건'], view:['건물관리']}),
  '총무':        boRolePerm({edit:['건물관리','안전보건','시스템 설정']}),        // 계정 · 권한 관리 담당
  '관리소장':    boRolePerm({edit:['건물관리','안전보건']}),
  '시설관리주임':boRolePerm({edit:['안전보건'], view:['건물관리']}),
  '경리':        boRolePerm({edit:['건물관리'], view:['안전보건']}),
  '미화원':      boRolePerm({view:['안전보건']}),                      // 본인 교육 · 서명 (나의 안전보건 리스트)
  '경비':        boRolePerm({view:['안전보건']}),
  '건물주':      boRolePerm({view:['건물관리','안전보건']})                      // 소유 건물만 · 조회 전용
};
/* 저장된 역할 권한이 없거나 그룹 구성이 다르면 기본값으로 채움 */
function boRolesValid(r){
  if(!r) return false;
  return BO_ROLES.every(function(role){ var a=r[role]; if(!a) return false; var k=Object.keys(a);
    return BO_GROUPS.every(function(g){ return BO_LEVELS.indexOf(a[g])>=0; }) && k.every(function(x){ return BO_GROUPS.indexOf(x)>=0; }); });
}
function boEnsureRoles(){
  var r=null; try{ r=JSON.parse(localStorage.getItem('buildone_roles')||'null'); }catch(e){}
  if(!boRolesValid(r)){ r=JSON.parse(JSON.stringify(BO_DEFAULT_ROLES)); localStorage.setItem('buildone_roles',JSON.stringify(r)); }
  return r;
}
/* 내 권한 (그룹 → none/view/edit) — 관리자는 전체 편집, 정해지지 않았으면 없음(거부) */
function v2Perm(group){ try{ var s=JSON.parse(localStorage.getItem('buildone_session')||'null'); if(!s) return 'none';
  if(s.role==='관리자') return 'edit'; var p=JSON.parse(localStorage.getItem('buildone_perm')||'null')||{}; return p[group]||'none'; }catch(e){ return 'none'; } }
function v2Deny(title){ document.body.innerHTML='<div style="max-width:520px;margin:80px auto;padding:28px;border:1px solid #e3e7ef;border-radius:12px;background:#fff;font-family:inherit;text-align:center">'
  +'<div style="font-size:34px">🔒</div><h2 style="margin:8px 0">'+title+' — 권한이 없습니다</h2><p style="color:#6b727c">이 계정에는 이 메뉴를 볼 권한이 없습니다. 시스템관리자에게 권한을 요청하세요.</p></div>'; }
