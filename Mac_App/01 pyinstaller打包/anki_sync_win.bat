@echo off

REM 检查 Anki 是否正在运行
tasklist /FI "IMAGENAME eq anki.exe" 2>NUL | find /I /N "anki.exe">NUL

REM 如果 Anki 已经在运行，直接进行同步；否则启动 Anki 并同步
if "%ERRORLEVEL%"=="0" (
    echo Anki已经运行，正在后台同步Anki卡片...
    curl http://localhost:8765 -X POST -H "Content-Type: application/json" -d "{\"action\": \"sync\", \"version\": 6}"
) else (
    echo 启动Anki...
    start /min "" "C:\Program Files\Anki\anki.exe"
    timeout /t 10 /nobreak > nul
    echo 正在后台同步Anki卡片...
    curl http://localhost:8765 -X POST -H "Content-Type: application/json" -d "{\"action\": \"sync\", \"version\": 6}"
)