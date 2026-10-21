@echo off
chcp 65001 >nul
title BuildOne 2.0 시연 서버
cd /d "%~dp0"
echo ==================================================
echo   BuildOne 2.0 시연 서버를 켭니다.
echo   잠시 후 브라우저에 로그인 화면이 열립니다.
echo   이 검은 창을 닫으면 시연 서버가 꺼집니다.
echo ==================================================
start "" "http://localhost:8900/00_%%EB%%A1%%9C%%EA%%B7%%B8%%EC%%9D%%B8.html"
python serve.py 8900
pause
