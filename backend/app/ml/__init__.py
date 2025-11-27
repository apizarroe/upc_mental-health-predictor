"""
Módulo de Machine Learning para detección de trastornos mentales.
Implementa Transformer (BERT/RoBERTa) + XGBoost para clasificación multi-etiqueta.
"""

from .preprocessor import TextPreprocessor
from .transformer_encoder import TransformerEncoder
from .classifier import DepressionClassifier
from .multi_label_classifier import MultiLabelMentalHealthClassifier
from .training_pipeline import TrainingPipeline
from .prediction_pipeline import PredictionPipeline

__all__ = [
    'TextPreprocessor',
    'TransformerEncoder',
    'DepressionClassifier',
    'MultiLabelMentalHealthClassifier',
    'TrainingPipeline',
    'PredictionPipeline'
]
