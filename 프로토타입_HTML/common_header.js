/* BuildOne 2.0 공통 머리줄 — [BuildOne · 메뉴 경로 · 로그인 사용자 · 로그아웃]
   통합메뉴(01) 위쪽의 경로 줄 · 사용자 표시를 각 화면의 어두운 머리줄로 옮김. 화면 맨 위 <header class="v2top">를 채우고, 없으면 새로 만듦. */
(function(){
  var css='header.v2top{background:#222730!important;color:#fff!important;padding:10px 20px!important;border:0!important;display:flex!important;align-items:center;gap:16px;}'
    +'header.v2top .logo{font-weight:700;font-size:19px;white-space:nowrap;}'
    +'header.v2top .v2crumb{color:#aab3c2;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}'
    +'header.v2top .v2crumb b{color:#fff;} header.v2top .v2crumb span{color:#5b6475!important;margin:0 4px;}'
    +'header.v2top .v2sp{flex:1;} header.v2top .v2who{font-size:14px;color:#cfd4dc;white-space:nowrap;display:inline-flex;align-items:center;gap:7px;}'
    +'header.v2top .v2ico{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;background:#fff;border-radius:5px;font-size:15px;line-height:1;}'   /* 어두운 바탕에서 사람 모양이 잘 보이게 흰 네모 위에 */
    +'header.v2top .v2out{border:1px solid #d0d5dd;background:#fff;color:#3b5bdb;border-radius:6px;padding:5px 12px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;}'
    +'header.v2top .v2old{display:none!important;}'
    +'header.v2top .v2crumb{min-width:0;flex:0 1 auto;} header.v2top .v2out,header.v2top .v2who,header.v2top #acctSw{flex:none;white-space:nowrap;}'   /* 좁으면 경로만 줄이고 버튼은 한 줄 */
    +'header.v2top #acctSw{background:#2f3542;color:#e9ecf2;border:1px solid #474e5c;border-radius:6px;padding:5px 8px;font-size:13px;font-family:inherit;max-width:230px;cursor:pointer;}';
  var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);
  function esc(t){ return String(t==null?'':t).replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  /* 시연 계정 전환 — 로그인 계정 목록(buildone_users)에서 골라 세션 · 메뉴 권한 · 기본 건물을 그 계정으로 바꾸고 전체 다시 열기 */
  function makeSwitcher(s){
    var users=[]; try{ users=(JSON.parse(localStorage.getItem('buildone_users')||'[]')||[]).filter(function(u){ return u.active!==false; }); }catch(e){}
    if(!users.length) return null;
    var sel=document.createElement('select'); sel.id='acctSw'; sel.title='시연용 — 다른 계정으로 바로 전환';
    sel.innerHTML='<option value="">🔁 시연 계정 전환</option>'+users.map(function(u){ return '<option value="'+esc(u.id)+'"'+(s&&s.id===u.id?' selected':'')+'>'+esc(u.role)+' · '+esc(u.name)+'</option>'; }).join('');
    sel.addEventListener('change',function(){
      var u=users.filter(function(x){ return x.id===sel.value; })[0]; if(!u) return;
      localStorage.setItem('buildone_session',JSON.stringify({id:u.id,name:u.name,role:u.role,buildings:u.buildings,worker:u.worker||'',at:new Date().toISOString()}));
      localStorage.setItem('buildone_user',u.name+' · '+u.role);
      try{ localStorage.setItem('buildone_perm',JSON.stringify((typeof boEnsureRoles==='function'?boEnsureRoles()[u.role]:null)||{})); }catch(e){}
      try{ var bl=JSON.parse(localStorage.getItem('buildone_buildings')||'[]'); if(Array.isArray(u.buildings)&&u.buildings.length){   /* 접근 건물 중 첫 건물로 */
        var i=bl.findIndex(function(b){ return u.buildings.indexOf(String(b.code))>=0; }); if(i>=0) localStorage.setItem('buildone_current_building',String(i)); } }catch(e){}
      (window.top||window).location.replace('01_통합메뉴.html?t='+Date.now());   /* 새 주소로 메뉴 다시 열기 — F5 없이 새 권한 · 새 화면 */
    });
    return sel;
  }
  function init(){
    var s=null; try{ s=JSON.parse(localStorage.getItem('buildone_session')||'null'); }catch(e){}
    var crumb=''; try{ if(window.parent!==window){ var c=window.parent.document.getElementById('crumb'); if(c) crumb=c.innerHTML; } }catch(e){}
    if(!crumb) crumb='<b>'+esc(document.title.replace(/^BuildOne 2\.0 — /,''))+'</b>';
    var hd=document.querySelector('header.v2top');
    if(!hd){ hd=document.createElement('header'); hd.className='v2top'; document.body.insertBefore(hd,document.body.firstChild); }
    var old=document.createElement('div'); old.className='v2old'; while(hd.firstChild) old.appendChild(hd.firstChild);   /* 원래 칸(id 등)은 숨겨서 보관 */
    var sw=old.querySelector('#acctSw');   /* 안전보건의 [시연 계정 전환]은 그 화면 것을 그대로 보이게 */
    hd.innerHTML='<div class="logo">BuildOne</div><div class="v2crumb">'+crumb+'</div><div class="v2sp"></div>'
      +(s?'<span class="v2who"><span class="v2ico">👤</span>'+esc(s.name)+' · '+esc(s.role)+'</span>':'')+'<button type="button" class="v2out">로그아웃</button>';
    if(!sw) sw=makeSwitcher(s);   /* 다른 화면에도 [시연 계정 전환] — 바꾸면 메뉴 권한도 그 계정으로 */
    if(sw) hd.insertBefore(sw,hd.querySelector('.v2who')||hd.querySelector('.v2out'));
    hd.appendChild(old);
    hd.querySelector('.v2out').addEventListener('click',function(){
      if(!confirm('로그아웃할까요?')) return;
      localStorage.removeItem('buildone_session'); (window.top||window).location.replace('00_로그인.html'); });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
