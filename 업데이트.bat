@echo off
cd /d "%~dp0"
title BuildOne 2.0 - GitHub 업데이트
echo ============================================================
echo    BuildOne 2.0  -  GitHub 업데이트 (받아오기 pull + 올리기 push)
echo ============================================================
echo.
if not exist ".git" (
  echo [안내] 아직 GitHub에 연결되지 않았습니다.
  echo        먼저  깃허브_최초연결.bat  을 한 번 실행하세요.
  echo.
  pause
  exit /b 1
)
git remote get-url origin >nul 2>&1
if errorlevel 1 (
  echo [안내] 아직 GitHub에 연결되지 않았습니다.
  echo        먼저  깃허브_최초연결.bat  을 한 번 실행하세요.
  echo.
  pause
  exit /b 1
)

rem ---------- 1) 이 컴퓨터에서 바뀐 내용 저장(commit) ----------
echo [1/3] 바뀐 내용을 확인합니다...
REM 날짜는 if 괄호 밖에서 미리 구함 (괄호 안에서 정하면 커밋 메시지에 비어 들어감)
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm"') do set STAMP=%%i
git add -A
git diff --cached --quiet
if errorlevel 1 (
  echo.
  echo === 이번에 반영되는 파일 ===
  git diff --cached --stat
  echo.
  git commit -q -m "update %STAMP%"
) else (
  echo       이 컴퓨터에서 바뀐 내용이 없습니다.
)
echo.

rem ---------- 2) GitHub 최신 내용 받아오기(pull) ----------
echo [2/3] GitHub의 최신 내용을 받아옵니다(pull)...
git pull --no-rebase --no-edit
if errorlevel 1 (
  echo.
  echo ============================================================
  echo  [중단] 받아오는 중 문제가 생겼습니다.
  echo   - 같은 파일을 다른 곳에서도 고친 경우 - 충돌 - 일 수 있습니다.
  echo   - 이 컴퓨터의 내용은 그대로 저장되어 있습니다.
  echo   - 이 메시지를 찍어 담당자에게 보내 주세요.
  echo ============================================================
  git merge --abort >nul 2>&1
  echo.
  pause
  exit /b 1
)
echo.

rem ---------- 3) GitHub에 올리기(push) ----------
set AHEAD=0
for /f %%n in ('git rev-list --count @{u}..HEAD 2^>nul') do set AHEAD=%%n
if "%AHEAD%"=="0" (
  echo [3/3] 올릴 내용이 없습니다. GitHub와 같은 최신 상태입니다.
  echo.
  pause
  exit /b 0
)
echo [3/3] GitHub에 올립니다(push)...
git push
if errorlevel 1 (
  echo.
  echo [실패] 올리지 못했습니다. 위 오류 메시지를 확인하세요.
  echo.
  pause
  exit /b 1
)
echo.
echo ============================================================
echo  완료!  최신 내용을 받아오고, GitHub에 반영했습니다.
echo ============================================================
echo.
pause
