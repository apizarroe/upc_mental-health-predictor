"""
Schemas Pydantic para el endpoint de predicción de salud mental.
Define la estructura de request y response del API.
Soporta predicción multi-etiqueta (depresión + ansiedad).
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, Optional, List
from datetime import datetime


class MentalHealthPredictionRequest(BaseModel):
    """Request para predicción de salud mental con 4 respuestas del paciente."""

    patient_id: Optional[str] = Field(
        default=None,
        description="ID del paciente (opcional, para tracking)"
    )

    answers: Dict[str, str] = Field(
        ...,
        description="4 respuestas del paciente sobre cómo se siente en diferentes aspectos",
        json_schema_extra={
            "example": {
                "question1": "Me siento cansado todo el tiempo y sin energía",
                "question2": "No tengo motivación para hacer nada",
                "question3": "Duermo mal y me despierto varias veces",
                "question4": "Me siento solo aunque esté con gente"
            }
        }
    )

    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v):
        """Valida que haya exactamente 4 respuestas no vacías."""
        if len(v) != 4:
            raise ValueError('Se requieren exactamente 4 respuestas')

        for key, value in v.items():
            if not value or not value.strip():
                raise ValueError(f'La respuesta "{key}" no puede estar vacía')

        for key, value in v.items():
            if len(value.strip()) < 5:
                raise ValueError(
                    f'La respuesta "{key}" es demasiado corta (mínimo 5 caracteres)'
                )

        return v


# Alias para retrocompatibilidad
DepressionPredictionRequest = MentalHealthPredictionRequest


class ConditionPrediction(BaseModel):
    """Predicción para una condición específica (depresión o ansiedad)."""

    has_condition: bool = Field(
        description="Indica si se detectaron indicadores de esta condición"
    )
    probability: float = Field(
        description="Probabilidad de la condición (0.0 a 1.0)",
        ge=0.0,
        le=1.0
    )
    confidence: float = Field(
        description="Nivel de confianza del modelo (0.0 a 1.0)",
        ge=0.0,
        le=1.0
    )
    label: str = Field(
        description="Etiqueta descriptiva de la predicción"
    )


class MultiLabelPredictions(BaseModel):
    """Predicciones multi-etiqueta para depresión y ansiedad."""

    depression: ConditionPrediction = Field(
        description="Predicción de depresión"
    )
    anxiety: ConditionPrediction = Field(
        description="Predicción de ansiedad"
    )


class PredictionSummary(BaseModel):
    """Resumen de las predicciones."""

    has_depression: bool = Field(
        description="Indica si se detectó depresión"
    )
    has_anxiety: bool = Field(
        description="Indica si se detectó ansiedad"
    )
    conditions_detected: List[str] = Field(
        description="Lista de condiciones detectadas",
        default_factory=list
    )
    interpretation: str = Field(
        description="Interpretación en lenguaje natural"
    )


class RiskSignal(BaseModel):
    """Señal de riesgo detectada en el texto del paciente."""
    tipo: str = Field(description="Tipo de señal: ideacion_suicida, autolesion, crisis_panico, etc.")
    frase: str = Field(description="Frase exacta que activó la señal")
    nivel: str = Field(description="Nivel de la señal: 'alto' o 'medio'")


class RiskAssessment(BaseModel):
    """Evaluación de riesgo clínico — capa independiente del clasificador ML."""
    nivel_riesgo: str = Field(description="Nivel global de riesgo: 'alto', 'medio' o 'bajo'")
    requiere_atencion: bool = Field(description="True si el especialista debe revisar con urgencia")
    señales_detectadas: List[RiskSignal] = Field(
        default_factory=list,
        description="Lista de señales de riesgo encontradas"
    )


class AnalysisDetails(BaseModel):
    """Detalles del análisis realizado."""

    combined_text_length: int = Field(
        description="Longitud del texto combinado analizado"
    )
    depression_keywords: List[str] = Field(
        description="Keywords de depresión detectadas",
        default_factory=list
    )
    anxiety_keywords: List[str] = Field(
        description="Keywords de ansiedad detectadas",
        default_factory=list
    )


class LabelMetrics(BaseModel):
    """Métricas para una etiqueta específica."""

    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None


class ModelMetrics(BaseModel):
    """Métricas del modelo multi-etiqueta."""

    depression: Optional[LabelMetrics] = None
    anxiety: Optional[LabelMetrics] = None
    overall: Optional[Dict[str, float]] = None


class ModelInfo(BaseModel):
    """Información del modelo utilizado."""
    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    model_type: str = Field(
        description="Tipo de modelo: 'binary' o 'multi_label'"
    )
    labels: List[str] = Field(
        description="Etiquetas que el modelo puede predecir"
    )
    bert_model: Optional[str] = None
    created_at: Optional[str] = None
    metrics: Optional[ModelMetrics] = None


class MentalHealthPredictionResponse(BaseModel):
    """Response completa de la predicción multi-etiqueta."""
    model_config = ConfigDict(protected_namespaces=())

    status: str = "success"
    patient_id: Optional[str] = None
    predictions: MultiLabelPredictions = Field(
        description="Predicciones para cada condición"
    )
    summary: PredictionSummary = Field(
        description="Resumen de las predicciones"
    )
    risk_assessment: RiskAssessment = Field(
        description="Evaluación de riesgo clínico (ideación suicida, crisis severa)"
    )
    analysis: AnalysisDetails = Field(
        description="Detalles del análisis"
    )
    model_info: ModelInfo = Field(
        description="Información del modelo utilizado"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "patient_id": "PAT-001",
                "predictions": {
                    "depression": {
                        "has_condition": True,
                        "probability": 0.78,
                        "confidence": 0.82,
                        "label": "Depresión"
                    },
                    "anxiety": {
                        "has_condition": True,
                        "probability": 0.65,
                        "confidence": 0.71,
                        "label": "Ansiedad"
                    }
                },
                "summary": {
                    "has_depression": True,
                    "has_anxiety": True,
                    "conditions_detected": ["depression", "anxiety"],
                    "interpretation": "Se detectaron indicadores de depresión y ansiedad"
                },
                "analysis": {
                    "combined_text_length": 234,
                    "depression_keywords": ["cansado", "energía", "solo"],
                    "anxiety_keywords": ["nervioso", "preocupado"]
                },
                "model_info": {
                    "model_name": "mental_health_multilabel_20251121",
                    "model_type": "multi_label",
                    "labels": ["depression", "anxiety"],
                    "bert_model": "dccuchile/bert-base-spanish-wwm-cased",
                    "metrics": {
                        "depression": {"accuracy": 0.75, "f1_score": 0.72},
                        "anxiety": {"accuracy": 0.73, "f1_score": 0.70}
                    }
                },
                "timestamp": "2025-11-21T15:30:00Z"
            }
        }
    )


# Alias para retrocompatibilidad
DepressionPredictionResponse = MentalHealthPredictionResponse
