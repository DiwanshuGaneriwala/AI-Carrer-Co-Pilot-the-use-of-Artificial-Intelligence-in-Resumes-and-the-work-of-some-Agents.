@echo off
setlocal
title AI Career Co-Pilot Launcher
set "APP_DIR=%~dp0"
set "PYTHON_EXE=python"
if exist "%APP_DIR%venv\Scripts\python.exe" set "PYTHON_EXE=%APP_DIR%venv\Scripts\python.exe"
set "HF_HOME=%TEMP%\huggingface"
if not exist "%HF_HOME%" mkdir "%HF_HOME%" >nul 2>&1

echo ===================================================
echo Starting AI Career Co-Pilot...
echo ===================================================

"%PYTHON_EXE%" -m uvicorn --version >nul 2>&1
if errorlevel 1 (
	echo ERROR: Uvicorn is not installed for "%PYTHON_EXE%".
	echo Install the Python dependencies with: python -m pip install -r requirements.txt
	pause
	exit /b 1
)

if not exist "%APP_DIR%my-react-app\node_modules\vite\bin\vite.js" (
	echo ERROR: Frontend dependencies are not installed.
	echo Run: npm --prefix my-react-app install
	pause
	exit /b 1
)

:: Start the backend in a separate terminal.
start "FastAPI Backend" cmd /k "cd /d ""%APP_DIR%"" && ""%PYTHON_EXE%"" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

:: Wait for the API to finish initializing its local models.
set /a WAIT_ATTEMPTS=0
:wait_for_backend
powershell -NoProfile -Command "try { $response = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/docs' -TimeoutSec 2; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 goto backend_ready
set /a WAIT_ATTEMPTS+=1
if %WAIT_ATTEMPTS% GEQ 120 goto backend_failed
timeout /t 1 /nobreak >nul
goto wait_for_backend

:backend_failed
echo ERROR: The API did not become ready within 120 seconds.
echo Check the FastAPI Backend window for model download or startup errors.
pause
exit /b 1

:backend_ready

start "React Frontend" cmd /k "cd /d ""%APP_DIR%my-react-app"" && npm run dev -- --host 127.0.0.1 --port 5173 --strictPort"
set /a FRONTEND_WAIT_ATTEMPTS=0
:wait_for_frontend
powershell -NoProfile -Command "try { $response = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:5173/' -TimeoutSec 2; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 goto frontend_ready
set /a FRONTEND_WAIT_ATTEMPTS+=1
if %FRONTEND_WAIT_ATTEMPTS% GEQ 30 goto frontend_failed
timeout /t 1 /nobreak >nul
goto wait_for_frontend

:frontend_failed
echo ERROR: The frontend did not become ready. Check the React Frontend window.
pause
exit /b 1

:frontend_ready
start "" http://localhost:5173

echo.
echo Backend launch requested at http://127.0.0.1:8000
echo Close the FastAPI Backend window to stop the server.
pause