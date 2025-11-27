"""
FastAPI application principal para Mental Health Predictor API.

Este servicio proporciona endpoints para predicción de depresión
usando un modelo BERT + XGBoost entrenado.
"""

# IMPORTANTE: Configurar variables de entorno ANTES de cualquier import
# Fix para macOS: Prevenir crash por conflicto entre libiomp5 y libomp
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '4'
os.environ['MKL_NUM_THREADS'] = '4'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import prediction, health
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Crear aplicación FastAPI
app = FastAPI(
    title="Mental Health Predictor API",
    description="""
    API para predicción de depresión usando modelo BERT + XGBoost.

    ## Características
    - Analiza 4 respuestas de texto de un paciente
    - Predice probabilidad de depresión
    - Modelo BERT en español: dccuchile/bert-base-spanish-wwm-cased
    - Precisión del modelo: ~85%

    ## Endpoints principales
    - `POST /api/v1/predict/depression` - Realizar predicción
    - `GET /api/v1/health` - Health check
    - `GET /api/v1/model/info` - Información del modelo

    ## Ejemplo de uso
    ```python
    import requests

    response = requests.post(
        "http://localhost:8000/api/v1/predict/depression",
        json={
            "patient_id": "PAT-001",
            "answers": {
                "question1": "Me siento cansado todo el tiempo",
                "question2": "No tengo motivación",
                "question3": "Duermo mal",
                "question4": "Me siento solo"
            }
        }
    )
    print(response.json())
    ```
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
# IMPORTANTE: En producción, especificar dominios permitidos exactos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: ["https://tu-dominio.com"]
    allow_credentials=True,
    allow_methods=["*"],  # En producción: ["GET", "POST"]
    allow_headers=["*"],
)

# Incluir routers
app.include_router(
    prediction.router,
    prefix="/api/v1",
    tags=["Prediction"]
)

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)


@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz del API.

    Returns:
        Información básica del servicio y enlaces útiles
    """
    return {
        "message": "Mental Health Predictor API",
        "version": "1.0.0",
        "description": "API para predicción de depresión usando BERT + XGBoost",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "health": "/api/v1/health",
            "predict": "/api/v1/predict/depression",
            "model_info": "/api/v1/model/info"
        }
    }


@app.on_event("startup")
async def startup_event():
    """
    Evento ejecutado al iniciar la aplicación.
    Pre-carga el modelo de ML para mejor performance.
    """
    print("=" * 80)
    print("🚀 Iniciando Mental Health Predictor API...")
    print("=" * 80)

    # Pre-cargar el modelo al iniciar (singleton)
    try:
        from app.core.dependencies import get_prediction_pipeline
        pipeline = get_prediction_pipeline()
        print("✅ Modelo de ML pre-cargado exitosamente")
        print(f"   • Modelo: {pipeline.get_model_info().get('model_name', 'unknown')}")
    except Exception as e:
        print(f"⚠️  Advertencia: No se pudo pre-cargar el modelo: {e}")
        print("   El modelo se cargará en la primera request")

    print("=" * 80)
    print("🎯 API lista para recibir requests")
    print("📚 Documentación disponible en: /docs")
    print("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento ejecutado al cerrar la aplicación."""
    print("\n" + "=" * 80)
    print("👋 Cerrando Mental Health Predictor API...")
    print("=" * 80)


# Exception handlers personalizados
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handler para rutas no encontradas."""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Endpoint no encontrado",
            "path": str(request.url),
            "available_endpoints": {
                "health": "/api/v1/health",
                "predict": "/api/v1/predict/depression",
                "model_info": "/api/v1/model/info",
                "docs": "/docs"
            }
        }
    )


if __name__ == "__main__":
    import uvicorn

    # Ejecutar servidor en desarrollo
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
