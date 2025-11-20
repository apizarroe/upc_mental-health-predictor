"""
Módulo de Machine Learning para detección de trastornos mentales.
Implementa BERT + XGBoost para clasificación de depresión.
"""

from .preprocessor import TextPreprocessor
from .bert_encoder import BERTEncoder
from .classifier import DepressionClassifier
from .training_pipeline import TrainingPipeline
from .prediction_pipeline import PredictionPipeline

__all__ = [
    'TextPreprocessor',
    'BERTEncoder',
    'DepressionClassifier',
    'TrainingPipeline',
    'PredictionPipeline'
]
