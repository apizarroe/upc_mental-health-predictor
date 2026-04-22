@echo off
echo Iniciando Mental Health Predictor API...
echo ===================================================

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    echo Activando entorno virtual desde backend\.venv...
    set PYTHON="%~dp0.venv\Scripts\python.exe"
) else if exist "..\.venv\Scripts\python.exe" (
    echo Activando entorno virtual desde raiz del proyecto...
    set PYTHON="%~dp0..\.venv\Scripts\python.exe"
) else (
    echo Error: No se encontro el entorno virtual .venv
    echo Ejecuta primero:
    echo   py -3.11 -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

%PYTHON% -c "import fastapi" 2>nul
if errorlevel 1 (
    echo FastAPI no esta instalado. Instalando dependencias...
    %PYTHON% -m pip install -r requirements.txt
)

set PORT=8000
if not "%1"=="" set PORT=%1

echo.
echo Configuracion:
echo   Host: 0.0.0.0
echo   Port: %PORT%
echo   Reload: enabled
echo.
echo Documentacion disponible en:
echo   Swagger UI: http://localhost:%PORT%/docs
echo   ReDoc:      http://localhost:%PORT%/redoc
echo.
echo ===================================================
echo Presiona Ctrl+C para detener el servidor
echo ===================================================
echo.

%PYTHON% -m uvicorn app.main:app --host 0.0.0.0 --port %PORT% --reload --log-level info
