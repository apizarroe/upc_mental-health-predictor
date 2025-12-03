"""
Dependency injection para FastAPI.
Maneja la inyección de dependencias reutilizables como el pipeline de predicción.
"""

from functools import lru_cache
from pathlib import Path
import sys
import logging

# Agregar el directorio backend al path para imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.ml.prediction_pipeline import PredictionPipeline
from app.ml.preprocessor import TextPreprocessor

logger = logging.getLogger(__name__)


@lru_cache()
def get_prediction_pipeline() -> PredictionPipeline:
    """
    Obtiene el pipeline de predicción (singleton).

    Se carga una sola vez al iniciar la aplicación y se reutiliza
    en todas las requests para mejor performance.

    Returns:
        PredictionPipeline: Instancia del pipeline de predicción

    Raises:
        FileNotFoundError: Si el modelo no está disponible
    """
    try:
        return PredictionPipeline(verbose=False)
    except FileNotFoundError as e:
        logger.error(f"Modelo no disponible: {e}")
        raise


@lru_cache()
def get_text_preprocessor() -> TextPreprocessor:
    """
    Obtiene el preprocesador de texto (singleton).

    Se crea una sola vez y se reutiliza en todas las requests
    para evitar recrear las listas de keywords.

    Returns:
        TextPreprocessor: Instancia del preprocesador
    """
    return TextPreprocessor()
