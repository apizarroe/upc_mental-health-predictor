#!/bin/bash
#
# Script wrapper para testear/validar el modelo BERT + XGBoost
# Configura automáticamente las variables de entorno necesarias para evitar crashes en macOS
#
# Uso:
#   ./run_testing.sh                      # 5 conversaciones aleatorias
#   ./run_testing.sh --random 10          # 10 conversaciones aleatorias
#   ./run_testing.sh --full-test          # Evaluación completa
#   ./run_testing.sh --indices 0 5 10     # Conversaciones específicas
#

set -e  # Salir si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}✅ VALIDACIÓN DE MODELO BERT + XGBOOST${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Verificar que estamos en el directorio backend
if [ ! -d "scripts" ]; then
    echo -e "${RED}❌ Error: Debes ejecutar este script desde el directorio backend${NC}"
    echo -e "${YELLOW}   cd backend && ./run_testing.sh${NC}"
    exit 1
fi

# Verificar que existe el entorno virtual (buscar en backend/ o en raíz)
VENV_PATH=""
if [ -d ".venv" ]; then
    VENV_PATH=".venv"
elif [ -d "../.venv" ]; then
    VENV_PATH="../.venv"
else
    echo -e "${RED}❌ Error: No se encontró el entorno virtual .venv${NC}"
    echo -e "${YELLOW}   Primero crea el entorno virtual:${NC}"
    echo -e "${YELLOW}   python3.11 -m venv .venv${NC}"
    echo -e "${YELLOW}   source .venv/bin/activate${NC}"
    echo -e "${YELLOW}   pip install -r requirements.txt${NC}"
    exit 1
fi

# Verificar que existe al menos un modelo entrenado
if [ ! -d "data/trained_models" ] || [ -z "$(ls -A data/trained_models/*.pkl 2>/dev/null)" ]; then
    echo -e "${YELLOW}⚠️  No se encontraron modelos entrenados${NC}"
    echo -e "${YELLOW}   Primero entrena un modelo:${NC}"
    echo -e "${YELLOW}   ./run_training.sh${NC}"
    exit 1
fi

# Configurar variables de entorno para evitar crash OpenMP (macOS)
echo -e "${GREEN}✅ Configurando variables de entorno (fix OpenMP)...${NC}"
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# Activar entorno virtual
echo -e "${GREEN}✅ Activando entorno virtual...${NC}"
source "$VENV_PATH/bin/activate"

# Verificar que Python está disponible
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Error: Python no está disponible en el entorno virtual${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python: $(python --version)${NC}"
echo -e "${GREEN}✅ Entorno: $(which python)${NC}\n"

# Ejecutar testing con todos los argumentos pasados al script
echo -e "${BLUE}🔍 Iniciando validación...${NC}\n"
python scripts/test.py "$@"

# Capturar código de salida
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}✅ ¡Validación completada exitosamente!${NC}\n"
else
    echo -e "\n${RED}❌ La validación finalizó con código de error: $EXIT_CODE${NC}"
    exit $EXIT_CODE
fi
