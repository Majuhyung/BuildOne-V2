# -*- coding: utf-8 -*-
"""BuildOne 2.0 시연 서버 — 프로토타입_HTML 폴더를 열고, 브라우저가 옛 화면을 기억(캐시)하지 않게 함
사용: python serve.py [포트]   (기본 8900)"""
import functools, http.server, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8900
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '프로토타입_HTML')


class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')   # 고친 화면이 바로 보이게
        super().end_headers()


if __name__ == '__main__':
    print(f'BuildOne 2.0 시연 서버: http://localhost:{PORT}/  (폴더 {ROOT})')
    http.server.ThreadingHTTPServer(('', PORT), functools.partial(NoCache, directory=ROOT)).serve_forever()
