@echo off
echo ============================================
echo   WHEELIE RACER - Starting Local Server...
echo ============================================
echo.
echo   Open browser to: http://localhost:8080/game.html
echo   Press Ctrl+C to stop
echo.
start http://localhost:8080/game.html
python -m http.server 8080
pause
