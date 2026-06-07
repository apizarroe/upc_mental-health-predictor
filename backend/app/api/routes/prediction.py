"""
Endpoint de predicción de salud mental.
Recibe 4 respuestas de un paciente y predice probabilidad de depresión y ansiedad.
Soporta modelos binarios (solo depresión) y multi-etiqueta (depresión + ansiedad).
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from app.api.schemas.prediction import (
    MentalHealthPredictionRequest,
    MentalHealthPredictionResponse,
    ConditionPrediction,
    MultiLabelPredictions,
    PredictionSummary,
    RiskAssessment,
    RiskSignal,
    AnalysisDetails,
    ModelInfo,
    ModelMetrics,
    LabelMetrics
)
from app.ml.prediction_pipeline import PredictionPipeline
from app.ml.preprocessor import TextPreprocessor
from app.core.dependencies import get_prediction_pipeline, get_text_preprocessor
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/predict/mental-health",
    response_model=MentalHealthPredictionResponse,
    summary="Predecir depresión y ansiedad basándose en 4 respuestas del paciente",
    description="""
    Analiza 4 respuestas de un paciente sobre cómo se siente en diferentes aspectos de su vida
    y predice la probabilidad de depresión Y ansiedad.

    Las 4 respuestas se concatenan para mantener el contexto completo del paciente,
    lo que permite al modelo entender mejor el estado emocional general.

    **Modelo utilizado:**
    - BERT: paraphrase-multilingual-MiniLM-L12-v2
    - Clasificador: Logistic Regression + keyword scores ponderados
    - Tipo: Multi-etiqueta (predice depresión y ansiedad simultáneamente)

    **Input esperado:**
    - 4 respuestas de texto (question1, question2, question3, question4)
    - Cada respuesta debe tener al menos 5 caracteres
    - patient_id es opcional

    **Output:**
    - predictions.depression: predicción de depresión con probabilidad y confianza
    - predictions.anxiety: predicción de ansiedad con probabilidad y confianza
    - summary: resumen con condiciones detectadas e interpretación
    - analysis: detalles del análisis (keywords detectadas por condición)
    - model_info: información del modelo utilizado
    """,
    responses={
        200: {
            "description": "Predicción exitosa",
            "content": {
                "application/json": {
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
                            "labels": ["depression", "anxiety"]
                        }
                    }
                }
            }
        },
        400: {"description": "Request inválido (respuestas faltantes o vacías)"},
        500: {"description": "Error interno del servidor"},
        503: {"description": "Modelo no disponible"}
    }
)
async def predict_mental_health(
    request: MentalHealthPredictionRequest,
    pipeline: PredictionPipeline = Depends(get_prediction_pipeline),
    preprocessor: TextPreprocessor = Depends(get_text_preprocessor)
) -> MentalHealthPredictionResponse:
    """
    Predice depresión y ansiedad basándose en 4 respuestas del paciente.

    Args:
        request: Objeto con las 4 respuestas del paciente
        pipeline: Pipeline de predicción (inyectado automáticamente)
        preprocessor: Preprocesador de texto (inyectado automáticamente)

    Returns:
        MentalHealthPredictionResponse con predicciones para ambas condiciones

    Raises:
        HTTPException: Si hay errores de validación o errores internos
    """
    try:
        # 1. Concatenar las 4 respuestas en un solo texto
        answer_texts = [
            request.answers.get("question1", ""),
            request.answers.get("question2", ""),
            request.answers.get("question3", ""),
            request.answers.get("question4", "")
        ]
        combined_text = " ".join(answer_texts)

        # 2. Realizar predicción con el pipeline
        result = pipeline.predict_text(
            text=combined_text,
            return_probabilities=True,
        )

        # 3. Detectar keywords por condición (usando singleton inyectado)
        keywords_by_condition = preprocessor.get_matched_keywords(combined_text)

        # 4. Obtener información del modelo
        model_info_raw = pipeline.get_model_info()

        # 5. Construir respuesta (siempre multi-label en el nuevo pipeline)
        if pipeline.is_multilabel_model():
            response = build_multilabel_response(
                result, request, combined_text,
                keywords_by_condition, model_info_raw
            )
        else:
            response = build_binary_response(
                result, request, combined_text,
                keywords_by_condition, model_info_raw
            )

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Modelo no disponible: {str(e)}"
        )

    except (AttributeError, KeyError, IndexError) as e:
        logger.error(f"Error en estructura de datos: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error procesando predicción"
        )

    except Exception as e:
        logger.exception(f"Error inesperado en predicción: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


# Mantener endpoint legacy para retrocompatibilidad
@router.post(
    "/predict/depression",
    response_model=MentalHealthPredictionResponse,
    summary="[LEGACY] Predecir depresión - Usar /predict/mental-health en su lugar",
    description="Endpoint mantenido por retrocompatibilidad. Usa /predict/mental-health para obtener predicciones de depresión y ansiedad.",
    deprecated=True
)
async def predict_depression(
    request: MentalHealthPredictionRequest,
    pipeline: PredictionPipeline = Depends(get_prediction_pipeline),
    preprocessor: TextPreprocessor = Depends(get_text_preprocessor)
) -> MentalHealthPredictionResponse:
    """Endpoint legacy que redirige a predict_mental_health."""
    return await predict_mental_health(request, pipeline, preprocessor)


def build_multilabel_response(
    result: Dict,
    request: MentalHealthPredictionRequest,
    combined_text: str,
    keywords_by_condition: Dict[str, List[str]],
    model_info_raw: Dict
) -> MentalHealthPredictionResponse:
    """Construye respuesta para modelo multi-etiqueta."""

    preds = result['predictions']
    summary = result['summary']

    # Generar interpretación
    interpretation = generate_multilabel_interpretation(
        summary['has_depression'],
        summary['has_anxiety'],
        preds['depression'].get('probability', 0),
        preds['anxiety'].get('probability', 0)
    )

    # Formatear métricas del modelo
    model_metrics = format_model_metrics(model_info_raw)

    risk_raw = result.get('risk_assessment', {})

    return MentalHealthPredictionResponse(
        status="success",
        patient_id=request.patient_id,
        predictions=MultiLabelPredictions(
            depression=ConditionPrediction(
                has_condition=preds['depression']['prediction'] == 1,
                probability=round(preds['depression'].get('probability', 0), 4),
                confidence=round(preds['depression'].get('confidence', 0), 4),
                label=preds['depression']['label']
            ),
            anxiety=ConditionPrediction(
                has_condition=preds['anxiety']['prediction'] == 1,
                probability=round(preds['anxiety'].get('probability', 0), 4),
                confidence=round(preds['anxiety'].get('confidence', 0), 4),
                label=preds['anxiety']['label']
            )
        ),
        summary=PredictionSummary(
            has_depression=summary['has_depression'],
            has_anxiety=summary['has_anxiety'],
            conditions_detected=summary['conditions_detected'],
            interpretation=interpretation
        ),
        risk_assessment=RiskAssessment(
            nivel_riesgo=risk_raw.get('nivel_riesgo', 'bajo'),
            requiere_atencion=risk_raw.get('requiere_atencion', False),
            señales_detectadas=[
                RiskSignal(tipo=s['tipo'], frase=s['frase'], nivel=s['nivel'])
                for s in risk_raw.get('señales_detectadas', [])
            ]
        ),
        analysis=AnalysisDetails(
            combined_text_length=len(combined_text),
            depression_keywords=keywords_by_condition.get('depression', [])[:10],
            anxiety_keywords=keywords_by_condition.get('anxiety', [])[:10]
        ),
        model_info=ModelInfo(
            model_name=model_info_raw.get("model_name", "unknown"),
            model_type=model_info_raw.get("model_type", "multi_label"),
            labels=model_info_raw.get("labels", ["depression", "anxiety"]),
            bert_model=model_info_raw.get("bert_model"),
            created_at=model_info_raw.get("created_at"),
            metrics=model_metrics
        ),
        timestamp=datetime.utcnow()
    )


def build_binary_response(
    result: Dict,
    request: MentalHealthPredictionRequest,
    combined_text: str,
    keywords_by_condition: Dict[str, List[str]],
    model_info_raw: Dict
) -> MentalHealthPredictionResponse:
    """Construye respuesta para modelo binario (solo depresión) en formato multi-etiqueta."""

    has_depression = result['prediction'] == 1
    probability = result.get('probability', 0)
    confidence = result.get('confidence', 0)

    # Generar interpretación
    interpretation = generate_binary_interpretation(probability, result['prediction'])

    # Formatear métricas del modelo
    model_metrics = format_model_metrics(model_info_raw)

    return MentalHealthPredictionResponse(
        status="success",
        patient_id=request.patient_id,
        predictions=MultiLabelPredictions(
            depression=ConditionPrediction(
                has_condition=has_depression,
                probability=round(probability, 4),
                confidence=round(confidence, 4),
                label=result['label']
            ),
            anxiety=ConditionPrediction(
                has_condition=False,
                probability=0.0,
                confidence=0.0,
                label="No disponible (modelo binario)"
            )
        ),
        summary=PredictionSummary(
            has_depression=has_depression,
            has_anxiety=False,
            conditions_detected=["depression"] if has_depression else [],
            interpretation=interpretation + " (Nota: modelo binario, ansiedad no evaluada)"
        ),
        analysis=AnalysisDetails(
            combined_text_length=len(combined_text),
            depression_keywords=keywords_by_condition.get('depression', [])[:10],
            anxiety_keywords=[]
        ),
        model_info=ModelInfo(
            model_name=model_info_raw.get("model_name", "unknown"),
            model_type="binary",
            labels=["depression"],
            bert_model=model_info_raw.get("bert_model"),
            created_at=model_info_raw.get("created_at"),
            metrics=model_metrics
        ),
        timestamp=datetime.utcnow()
    )


def format_model_metrics(model_info_raw: Dict) -> ModelMetrics:
    """Formatea las métricas del modelo para la respuesta."""
    metrics = model_info_raw.get("metrics", {})
    if not metrics:
        return None

    # Nuevo formato: métricas flat con f1_weighted, accuracy, etc.
    return ModelMetrics(
        depression=LabelMetrics(
            accuracy=metrics.get("accuracy"),
            precision=metrics.get("precision"),
            recall=metrics.get("recall"),
            f1_score=metrics.get("f1_weighted")
        ),
        anxiety=None,
        overall={"f1_weighted": metrics.get("f1_weighted")}
    )


def generate_multilabel_interpretation(
    has_depression: bool,
    has_anxiety: bool,
    prob_depression: float,
    prob_anxiety: float
) -> str:
    """Genera interpretación para predicción multi-etiqueta."""

    conditions = []
    if has_depression:
        conditions.append(f"depresión ({prob_depression:.0%})")
    if has_anxiety:
        conditions.append(f"ansiedad ({prob_anxiety:.0%})")

    if len(conditions) == 2:
        return f"Se detectaron indicadores de {conditions[0]} y {conditions[1]}. Se recomienda evaluación profesional."
    elif len(conditions) == 1:
        return f"Se detectaron indicadores de {conditions[0]}. Se recomienda seguimiento."
    else:
        if max(prob_depression, prob_anxiety) > 0.3:
            return "No se detectaron indicadores significativos, aunque hay algunos signos leves a monitorear."
        return "No se detectaron indicadores significativos de depresión ni ansiedad."


def generate_binary_interpretation(probability: float, prediction: int) -> str:
    """Genera interpretación para modelo binario (solo depresión)."""
    if prediction == 0:
        if probability < 0.2:
            return "No se detectaron indicadores significativos de depresión"
        else:
            return "Se detectaron algunos indicadores leves, pero no suficientes para sugerir depresión"
    else:
        if probability >= 0.8:
            return "Se detectaron indicadores de depresión con alta probabilidad"
        elif probability >= 0.6:
            return "Se detectaron indicadores moderados de depresión"
        else:
            return "Se detectaron algunos indicadores que sugieren posible depresión"
