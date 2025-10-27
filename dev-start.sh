#!/bin/bash

# Script para iniciar el entorno de desarrollo local
# Uso: ./dev-start.sh

echo "=========================================="
echo "Mental Health Predictor - Dev Environment"
echo "=========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar Node.js
if command_exists node; then
    echo -e "${GREEN}✓${NC} Node.js $(node --version) instalado"
else
    echo -e "${RED}✗${NC} Node.js no está instalado. Instálalo desde https://nodejs.org/"
    exit 1
fi

# Verificar Python
if command_exists python3; then
    echo -e "${GREEN}✓${NC} Python $(python3 --version) instalado"
else
    echo -e "${RED}✗${NC} Python 3 no está instalado"
    exit 1
fi

# Verificar PostgreSQL
if command_exists psql; then
    echo -e "${GREEN}✓${NC} PostgreSQL está instalado"
else
    echo -e "${YELLOW}⚠${NC} PostgreSQL no detectado. Asegúrate de tenerlo corriendo."
fi

echo ""
echo "=========================================="
echo "Iniciando servicios..."
echo "=========================================="
echo ""

# Verificar si existe .env en frontend
if [ ! -f "./frontend/.env" ]; then
    echo -e "${YELLOW}⚠${NC} No existe frontend/.env, copiando desde .env.example..."
    cp ./frontend/.env.example ./frontend/.env
    echo -e "${GREEN}✓${NC} Creado frontend/.env"
fi

# Verificar si existe .env en backend
if [ ! -f "./backend/.env" ]; then
    echo -e "${YELLOW}⚠${NC} No existe backend/.env, copiando desde .env.example..."
    cp ./backend/.env.example ./backend/.env
    echo -e "${GREEN}✓${NC} Creado backend/.env"
fi

# Crear directorio de logs si no existe
mkdir -p backend/logs

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo -e "${YELLOW}Deteniendo servicios...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar Backend ML
echo -e "${GREEN}[1/2]${NC} Iniciando Backend ML API (Python)..."
cd backend

# Verificar si existe venv
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC} Entorno virtual no encontrado. Creando..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Entorno virtual creado"
fi

# Activar venv e instalar dependencias
source venv/bin/activate
if [ ! -f "venv/.installed" ]; then
    echo "Instalando dependencias Python..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    touch venv/.installed
    echo -e "${GREEN}✓${NC} Dependencias instaladas"
fi

# Iniciar servidor en background
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

sleep 2

# Verificar si el backend está corriendo
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Backend ML corriendo en http://localhost:8000"
    echo -e "  Docs: http://localhost:8000/docs"
else
    echo -e "${RED}✗${NC} Error al iniciar backend. Ver logs en backend/logs/backend.log"
    exit 1
fi

# Iniciar Frontend
echo -e "${GREEN}[2/2]${NC} Iniciando Frontend (SvelteKit)..."
cd frontend

# Verificar si node_modules existe
if [ ! -d "node_modules" ]; then
    echo "Instalando dependencias Node.js..."
    npm install
    echo -e "${GREEN}✓${NC} Dependencias instaladas"
fi

# Iniciar servidor en background
npm run dev > ../backend/logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 3

# Verificar si el frontend está corriendo
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Frontend corriendo en http://localhost:5173"
else
    echo -e "${RED}✗${NC} Error al iniciar frontend. Ver logs en backend/logs/frontend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}¡Entorno de desarrollo listo!${NC}"
echo "=========================================="
echo ""
echo "Servicios corriendo:"
echo "  → Frontend:  http://localhost:5173"
echo "  → Backend:   http://localhost:8000"
echo "  → API Docs:  http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener todos los servicios"
echo ""

# Mantener el script corriendo
wait
