@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON=py -3"
) else (
  set "PYTHON=python"
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating local virtual environment...
  %PYTHON% -m venv .venv
  if errorlevel 1 goto :failed
)
call .venv\Scripts\activate.bat
echo Installing or updating required packages...
python -m pip install -r requirements.txt
if errorlevel 1 goto :failed
echo Starting Bombas Grading Studio...
python -m streamlit run app.py
if errorlevel 1 goto :failed
exit /b 0
:failed
echo.
echo Setup failed. Install Python 3.10 or newer from python.org and retry.
pause
exit /b 1
