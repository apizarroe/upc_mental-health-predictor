#!/bin/bash

# Script para ejecutar el API de predicción de depresión
# Activa el entorno virtual y ejecuta uvicorn

echo "🚀 Iniciando Mental Health Predictor API..."
echo "═══════════════════════════════════════════════════════════"

# Obtener directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activar entorno virtual (buscar en backend y en raíz del proyecto)
if [ -d ".venv" ]; then
    echo "✅ Activando entorno virtual desde backend/.venv..."
    source .venv/bin/activate
elif [ -d "../.venv" ]; then
    echo "✅ Activando entorno virtual desde raíz del proyecto..."
    source ../.venv/bin/activate
else
    echo "❌ Error: No se encontró el entorno virtual .venv"
    echo "   Ejecuta primero: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Verificar que FastAPI y Uvicorn estén instalados
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI no está instalado. Instalando..."
    pip install fastapi uvicorn[standard]
fi

# Verificar que el modelo exista
if [ ! -d "data/trained_models" ] || [ -z "$(ls -A data/trained_models/*.pkl 2>/dev/null)" ]; then
    echo "⚠️  Advertencia: No se encontró ningún modelo entrenado"
    echo "   Entrena un modelo primero con: ./run_training.sh"
    echo ""
    read -p "¿Deseas continuar de todas formas? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Configurar puerto (default: 8000)
PORT=${1:-8000}

echo ""
echo "🎯 Configuración:"
echo "   • Host: 0.0.0.0"
echo "   • Port: $PORT"
echo "   • Reload: enabled (modo desarrollo)"
echo ""
echo "📚 Documentación disponible en:"
echo "   • Swagger UI: http://localhost:$PORT/docs"
echo "   • ReDoc: http://localhost:$PORT/redoc"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Presiona Ctrl+C para detener el servidor"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Ejecutar servidor con uvicorn
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --reload \
    --log-level info
