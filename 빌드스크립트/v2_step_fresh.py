# -*- coding: utf-8 -*-
# build_v2.py 끝에서 exec — 로그인 후 · 메뉴 클릭 때 항상 새 화면(브라우저가 기억한 옛 화면 대신)
import io as _io, os as _os

def _patch(name, pairs):
    p = _os.path.join(OUT, name)
    t = _io.open(p, encoding='utf-8').read().replace('\r\n', '\n')
    for a, b, n in pairs:
        assert t.count(a) == n, f'{name}: {t.count(a)}x {a[:60]}'
        t = t.replace(a, b)
    open(p, 'wb').write(t.replace('\n', '\r\n').encode('utf-8'))

# 로그인 → 메뉴: 새 주소로
_patch('00_로그인.html', [("location.href=HOME", "location.href=HOME+'?t='+Date.now()", 2)])
# 메뉴 → 화면: 열 때마다 새 주소로 (#탭은 그대로)
_patch('01_통합메뉴.html', [("<iframe src=\"${k.link}${k.tab?'#'+k.tab:''}\"", "<iframe src=\"${k.link}?t=${Date.now()}${k.tab?'#'+k.tab:''}\"", 1)])
print('항상 새 화면: 로그인 · 메뉴 클릭')
