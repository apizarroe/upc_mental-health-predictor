@echo off
REM Script para iniciar el entorno de desarrollo local en Windows
REM Uso: dev-start.bat

echo ==========================================
echo Mental Health Predictor - Dev Environment
echo ==========================================
echo.

REM Verificar Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Node.js no esta instalado. Instalalo desde https://nodejs.org/
    exit /b 1
)
echo [OK] Node.js instalado

REM Verificar Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python no esta instalado
    exit /b 1
)
echo [OK] Python instalado

echo.
echo ==========================================
echo Iniciando servicios...
echo ==========================================
echo.

REM Verificar .env en frontend
if not exist "frontend\.env" (
    echo [!] No existe frontend\.env, copiando desde .env.example...
    copy frontend\.env.example frontend\.env
    echo [OK] Creado frontend\.env
)

REM Verificar .env en backend
if not exist "backend\.env" (
    echo [!] No existe backend\.env, copiando desde .env.example...
    copy backend\.env.example backend\.env
    echo [OK] Creado backend\.env
)

REM Crear directorio de logs
if not exist "backend\logs" mkdir backend\logs

REM Iniciar Backend ML
echo [1/2] Iniciando Backend ML API (Python)...
cd backend

REM Verificar y crear venv
if not exist "venv" (
    echo [!] Entorno virtual no encontrado. Creando...
    python -m venv venv
    echo [OK] Entorno virtual creado
)

REM Activar venv e instalar dependencias
call venv\Scripts\activate.bat
if not exist "venv\.installed" (
    echo Instalando dependencias Python...
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo. > venv\.installed
    echo [OK] Dependencias instaladas
)

REM Iniciar backend
start "Backend ML API" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

timeout /t 3 /nobreak >nul

REM Iniciar Frontend
echo [2/2] Iniciando Frontend (SvelteKit)...
cd frontend

REM Verificar node_modules
if not exist "node_modules" (
    echo Instalando dependencias Node.js...
    call npm install
    echo [OK] Dependencias instaladas
)

REM Iniciar frontend
start "Frontend SvelteKit" cmd /k "npm run dev"
cd ..

timeout /t 3 /nobreak >nul

echo.
echo ==========================================
echo Entorno de desarrollo listo!
echo ==========================================
echo.
echo Servicios corriendo:
echo   - Frontend:  http://localhost:5173
echo   - Backend:   http://localhost:8000
echo   - API Docs:  http://localhost:8000/docs
echo.
echo Presiona cualquier tecla para salir (cierra las ventanas manualmente)
pause >nul
