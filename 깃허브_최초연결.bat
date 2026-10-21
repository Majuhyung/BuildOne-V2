@echo off
cd /d "%~dp0"
title BuildOne 2.0 - GitHub 최초 연결
echo ============================================================
echo    BuildOne 2.0  -  GitHub 최초 연결  (딱 한 번만 실행)
echo ============================================================
echo.
where git >nul 2>&1
if errorlevel 1 (
  echo [중단] Git이 설치되어 있지 않습니다. https://git-scm.com 에서 설치한 뒤 다시 실행하세요.
  echo.
  pause
  exit /b 1
)

REM ---------- 1) 이 폴더를 Git 저장소로 (처음 한 번) ----------
if not exist ".git" (
  echo [준비] 이 폴더를 Git 저장소로 만듭니다...
  git init -q
  git symbolic-ref HEAD refs/heads/main
)

REM ---------- 2) 커밋 작성자 - 없으면 V1 빌드원시스템 설정을 그대로, 그것도 없으면 물어봄 ----------
set "GUN="
for /f "delims=" %%n in ('git config user.name 2^>nul') do set "GUN=%%n"
if not "%GUN%"=="" goto IDOK
for /f "delims=" %%n in ('git -C "..\빌드원시스템" config user.name 2^>nul') do git config user.name "%%n"
for /f "delims=" %%e in ('git -C "..\빌드원시스템" config user.email 2^>nul') do git config user.email "%%e"
for /f "delims=" %%n in ('git config user.name 2^>nul') do set "GUN=%%n"
if not "%GUN%"=="" goto IDOK
echo 커밋에 남길 이름과 이메일을 입력하세요. (GitHub 계정과 같게)
set "GUN="
set /p GUN=이름:
set "GUE="
set /p GUE=이메일:
if "%GUN%"=="" (
  echo [중단] 이름이 없으면 커밋할 수 없습니다.
  pause
  exit /b 1
)
git config user.name "%GUN%"
git config user.email "%GUE%"
:IDOK
echo 커밋 작성자: %GUN%
echo.

REM ---------- 3) 지금 파일을 커밋 ----------
echo [1/2] 지금 파일을 저장(commit)합니다...
REM 날짜는 if 괄호 밖에서 미리 구함 (괄호 안에서 정하면 커밋 메시지에 비어 들어감)
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm"') do set STAMP=%%i
git add -A
git diff --cached --quiet
if errorlevel 1 (
  git commit -q -m "BuildOne 2.0 %STAMP%"
) else (
  echo       새로 저장할 변경이 없습니다.
)
git rev-parse --verify --quiet HEAD >nul 2>&1
if errorlevel 1 (
  echo [중단] 첫 저장을 만들지 못했습니다. 위 메시지를 확인하세요.
  echo.
  pause
  exit /b 1
)
git branch -M main
echo.

REM ---------- 4) GitHub 저장소 연결 ----------
echo [2/2] GitHub 저장소 주소(URL)를 붙여넣고 Enter 를 누르세요.
echo    예) https://github.com/PlatformForge-dev/buildone-v2.git
echo    * V1 저장소 buildone-plan 이 아닌 2.0용 새 저장소를 권장합니다.
echo    * GitHub에서 저장소를 만들 때 README 추가는 체크하지 마세요.
echo    (이미 연결돼 있으면 그냥 Enter 만 누르면 됩니다)
echo.
set "REPO="
set /p REPO=저장소 URL:

REM 입력이 없으면 기존 연결(origin) 사용
if "%REPO%"=="" (
  for /f "delims=" %%u in ('git remote get-url origin 2^>nul') do set "REPO=%%u"
)
if "%REPO%"=="" (
  echo.
  echo [중단] URL이 없고 기존 연결도 없습니다. 주소를 입력해 다시 실행하세요.
  echo        이 컴퓨터의 저장은 끝났습니다. GitHub에만 아직 안 올라갔습니다.
  echo.
  pause
  exit /b 1
)

REM 브라우저 주소(.../tree/...) 를 붙여넣어도 자동 정리
set "REPO=%REPO:/tree/=|%"
for /f "tokens=1 delims=|" %%a in ("%REPO%") do set "REPO=%%a"
if "%REPO:~-1%"=="/" set "REPO=%REPO:~0,-1%"
if /i not "%REPO:~-4%"==".git" set "REPO=%REPO%.git"

echo.
echo 연결할 저장소: %REPO%
echo %REPO% | find /i "buildone-plan" >nul
if not errorlevel 1 (
  echo.
  echo [주의] V1 저장소 buildone-plan 입니다. 2.0은 새 저장소에 올리는 것을 권장합니다.
  echo        계속하면 아래에서 V1 기록을 덮어쓸지 한 번 더 묻습니다.
)
echo.
git remote remove origin >nul 2>&1
git remote add origin %REPO%

echo 원격 저장소 상태를 확인합니다...
git fetch origin >nul 2>&1
if errorlevel 1 (
  echo [안내] 원격 정보를 못 받아왔습니다. 처음 연결이거나 로그인 전일 수 있습니다.
  echo        덮어쓰지 않고 일반 업로드만 시도합니다.
)
echo.

REM 원격에 main 브랜치가 아직 없으면 그냥 올리면 된다
git rev-parse --verify --quiet refs/remotes/origin/main >nul 2>&1
if errorlevel 1 (
  echo [확인] 원격이 비어 있습니다. 그냥 올립니다.
  goto SAFEPUSH
)

REM 원격에만 있는 커밋이 몇 개인지 = 덮어쓰면 사라지는 커밋
set "LOST=0"
for /f %%n in ('git rev-list --count origin/main --not main 2^>nul') do set "LOST=%%n"
if "%LOST%"=="0" (
  echo [확인] 사라지는 원격 커밋이 없습니다. 안전하게 올립니다.
  goto SAFEPUSH
)

REM ===== 여기부터는 원격 작업이 사라지는 위험한 상황 =====
echo ############################################################
echo  [경고] 원격에만 있는 커밋 %LOST% 개가 덮어쓰면 사라집니다!
echo ############################################################
echo.
echo  사라지게 되는 원격 커밋:
echo  ------------------------------------------------------------
git log --oneline --no-decorate --max-count=20 origin/main --not main
echo  ------------------------------------------------------------
echo.
echo  * 저장소 주소가 맞는지 먼저 확인하세요.
echo  * 다른 PC에서 올린 2.0 작업이라면 지금 취소하고  업데이트.bat  을 실행하세요.
echo  * 원격 내용을 정말 지워도 될 때만 덮어쓰세요.
echo.
set "OK="
set /p OK=정말 덮어쓰려면 OVERWRITE 를 그대로 입력하세요:
if /i not "%OK%"=="OVERWRITE" (
  echo.
  echo 취소되었습니다. 원격은 그대로입니다.
  echo.
  pause
  exit /b 0
)
echo.
echo 업로드 중... 덮어쓰기
echo.
REM --force-with-lease : 확인한 뒤 남이 새로 올린 게 있으면 실패시켜 사고를 막는다
git push -u origin main --force-with-lease
if errorlevel 1 (
  echo.
  echo [실패] 확인한 뒤에 원격이 또 바뀌었거나 거부되었습니다.
  echo        아무것도 덮어쓰지 않았습니다. 다시 상태를 확인하세요.
  echo.
  pause
  exit /b 1
)
goto DONE

:SAFEPUSH
echo GitHub 로그인 창이 뜨면 로그인하세요. 최초 1회
echo 업로드 중...
echo.
git push -u origin main
if errorlevel 1 (
  echo.
  echo [실패] 위의 오류 메시지를 확인하세요. URL / 로그인 / 네트워크 확인
  echo.
  pause
  exit /b 1
)

:DONE
echo.
echo ============================================================
echo  연결 완료!  다음부터는  업데이트.bat  만 실행하면 됩니다.
echo ============================================================
echo.
pause
