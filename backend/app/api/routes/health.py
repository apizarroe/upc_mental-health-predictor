"""
Endpoints de health check y información del sistema.
"""

from fastapi import APIRouter, Depends
from app.core.dependencies import get_prediction_pipeline
from app.ml.prediction_pipeline import PredictionPipeline
from datetime import datetime
from typing import Dict, Any

router = APIRouter()


@router.get(
    "/health",
    summary="Health check del servicio",
    description="Verifica que el servicio esté funcionando correctamente",
    response_description="Estado del servicio"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check básico del servicio.

    Returns:
        Diccionario con estado del servicio
    """
    return {
        "status": "healthy",
        "service": "Mental Health Predictor API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/model/info",
    summary="Información del modelo ML",
    description="Obtiene información detallada del modelo de predicción cargado",
    response_description="Metadata del modelo"
)
async def model_info(
    pipeline: PredictionPipeline = Depends(get_prediction_pipeline)
) -> Dict[str, Any]:
    """
    Obtiene información del modelo de ML cargado.

    Args:
        pipeline: Pipeline de predicción (inyectado)

    Returns:
        Diccionario con metadata del modelo
    """
    info = pipeline.get_model_info()

    # Formatear métricas si existen
    formatted_info = {
        "status": "success",
        "model": {
            "name": info.get("model_name"),
            "bert_model": info.get("bert_model"),
            "created_at": info.get("created_at"),
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    # Agregar métricas si existen
    if info.get("metrics"):
        formatted_info["model"]["metrics"] = info["metrics"]

    return formatted_info


@router.get(
    "/",
    summary="Root endpoint",
    description="Endpoint raíz del API"
)
async def root() -> Dict[str, Any]:
    """
    Endpoint raíz con información básica del API.

    Returns:
        Información básica del servicio
    """
    return {
        "message": "Mental Health Predictor API",
        "version": "1.0.0",
        "description": "API para predicción de depresión y ansiedad usando MiniLM + Logistic Regression",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/v1/health",
            "predict": "/api/v1/predict/depression",
            "model_info": "/api/v1/model/info"
        }
    }
