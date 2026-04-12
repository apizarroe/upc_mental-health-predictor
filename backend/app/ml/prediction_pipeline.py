"""
Pipeline completo de predicción: BERT + XGBoost
para detección de trastornos mentales.
Soporta modelos binarios (solo depresión) y multi-etiqueta (depresión + ansiedad).
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import json
import sys
import os

from .transformer_encoder import TransformerEncoder
from .classifier import DepressionClassifier
from .multi_label_classifier import MultiLabelMentalHealthClassifier
from .text_processing import clean_text


class PredictionPipeline:
    """
    Pipeline completo para predicción con modelo entrenado.

    Soporta modelos binarios (solo depresión) y multi-etiqueta (depresión + ansiedad).
    Auto-detecta el tipo de modelo basándose en los metadatos.

    Uso:
        # Con modelo por defecto (el más reciente)
        pipeline = PredictionPipeline()
        result = pipeline.predict_text("Me siento muy triste últimamente")

        # El resultado incluirá depresión y ansiedad si el modelo es multi-etiqueta
    """

    DEFAULT_THRESHOLDS = {
        'depression': 0.80,
        'anxiety': 0.75
    }

    def __init__(
        self,
        model_path: Optional[str] = None,
        models_dir: str = "data/trained_models",
        verbose: bool = True
    ):
        """
        Inicializa el pipeline de predicción.

        Args:
            model_path: Ruta específica al modelo .pkl (si None, usa el más reciente)
            models_dir: Directorio donde buscar modelos
            verbose: Mostrar información de carga
        """
        self.models_dir = Path(models_dir)
        self.verbose = verbose

        # Componentes del pipeline
        self.encoder: Optional[TransformerEncoder] = None
        self.classifier: Union[DepressionClassifier, MultiLabelMentalHealthClassifier] = None

        # Metadata del modelo
        self.metadata: Optional[Dict] = None
        self.model_name: Optional[str] = None
        self.is_multi_label: bool = False
        self.labels: List[str] = ['depression']
        self.thresholds: Dict[str, float] = dict(self.DEFAULT_THRESHOLDS)

        # Cargar modelo
        if model_path:
            self._load_model(model_path)
        else:
            self._load_latest_model()

    def _load_latest_model(self):
        """Carga el modelo más reciente del directorio de modelos."""
        if not self.models_dir.exists():
            raise FileNotFoundError(
                f"No se encontró el directorio de modelos: {self.models_dir}\n"
                "Primero entrena un modelo con: python scripts/train.py"
            )

        # Buscar archivos .pkl (multi-label y binarios)
        model_files = list(self.models_dir.glob("mental_health_multilabel_*.pkl"))
        model_files.extend(list(self.models_dir.glob("depression_bert_xgboost_*.pkl")))

        if not model_files:
            raise FileNotFoundError(
                f"No se encontraron modelos entrenados en {self.models_dir}\n"
                "Primero entrena un modelo con: python scripts/train.py"
            )

        # Ordenar por fecha de modificación y tomar el más reciente
        latest_model = max(model_files, key=lambda p: p.stat().st_mtime)

        if self.verbose:
            print(f"📂 Cargando modelo más reciente: {latest_model.name}")

        self._load_model(str(latest_model))

    def _load_model(self, model_path: str):
        """
        Carga un modelo entrenado específico y su configuración.

        Args:
            model_path: Ruta al archivo .pkl del modelo
        """
        model_file = Path(model_path)

        if not model_file.exists():
            raise FileNotFoundError(f"No se encontró el modelo: {model_path}")

        self.model_name = model_file.stem

        # Cargar metadata para obtener configuración
        metadata_file = model_file.parent / f"{model_file.stem}_metadata.json"

        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)

            # Detectar tipo de modelo
            self.is_multi_label = self.metadata.get('model_type') == 'multi_label'
            self.labels = self.metadata.get('labels', ['depression'])
            self.thresholds = self._resolve_thresholds(self.metadata)

            bert_model = self.metadata.get('bert_model', 'dccuchile/bert-base-spanish-wwm-cased')
            max_length = self.metadata.get('max_length', 512)

            if self.verbose:
                print(f"\n📋 Configuración del modelo:")
                print(f"   • Nombre: {self.model_name}")
                print(f"   • Tipo: {'Multi-Etiqueta' if self.is_multi_label else 'Binario'}")
                print(f"   • Etiquetas: {self.labels}")
                print(f"   • BERT model: {bert_model}")
                print(f"   • Max length: {max_length}")
                print(f"   • Thresholds: {self.thresholds}")
                print(f"   • Entrenado: {self.metadata.get('created_at', 'N/A')}")

                # Mostrar métricas si existen
                if 'metrics' in self.metadata and 'test' in self.metadata['metrics']:
                    test_metrics = self.metadata['metrics']['test']
                    print(f"\n📊 Métricas del modelo (Test Set):")

                    if self.is_multi_label:
                        # Métricas por etiqueta
                        for label in self.labels:
                            if label in test_metrics:
                                m = test_metrics[label]
                                print(f"   📌 {label.upper()}:")
                                print(f"      • Accuracy:  {m.get('accuracy', 'N/A'):.4f}")
                                print(f"      • F1-Score:  {m.get('f1_score', 'N/A'):.4f}")
                    else:
                        print(f"   • Accuracy:  {test_metrics.get('accuracy', 'N/A'):.4f}")
                        print(f"   • Precision: {test_metrics.get('precision', 'N/A'):.4f}")
                        print(f"   • Recall:    {test_metrics.get('recall', 'N/A'):.4f}")
                        print(f"   • F1-Score:  {test_metrics.get('f1_score', 'N/A'):.4f}")

            # Inicializar encoder Transformer
            self.encoder = TransformerEncoder(
                model_name=bert_model,
                max_length=max_length,
                batch_size=16
            )
        else:
            if self.verbose:
                print("⚠️  No se encontró archivo de metadata, usando configuración default")
            self.thresholds = self._resolve_thresholds()
            self.encoder = TransformerEncoder()

        # Cargar clasificador según tipo
        if self.is_multi_label:
            self.classifier = MultiLabelMentalHealthClassifier()
        else:
            self.classifier = DepressionClassifier()

        self.classifier.load(str(model_file))

        if self.verbose:
            print("\n✅ Pipeline de predicción listo!")

    def _resolve_thresholds(self, metadata: Optional[Dict] = None) -> Dict[str, float]:
        """Resuelve umbrales de decisión desde metadata/env o usa defaults conservadores."""
        thresholds = dict(self.DEFAULT_THRESHOLDS)

        if metadata:
            thresholds.update(metadata.get('decision_thresholds', {}))

        env_depression = os.getenv('ML_DEPRESSION_THRESHOLD')
        env_anxiety = os.getenv('ML_ANXIETY_THRESHOLD')

        if env_depression is not None:
            thresholds['depression'] = float(env_depression)
        if env_anxiety is not None:
            thresholds['anxiety'] = float(env_anxiety)

        return {
            label: min(max(float(value), 0.0), 1.0)
            for label, value in thresholds.items()
        }

    def predict_text(
        self,
        text: str,
        return_probabilities: bool = True,
        clean_input: bool = True
    ) -> Dict:
        """
        Predice trastornos mentales para un texto dado.

        Args:
            text: Texto a analizar
            return_probabilities: Incluir probabilidades en la respuesta
            clean_input: Aplicar limpieza de texto antes de predecir

        Returns:
            Para modelo multi-etiqueta:
            {
                'text': str,
                'predictions': {
                    'depression': {'prediction': int, 'probability': float, 'label': str},
                    'anxiety': {'prediction': int, 'probability': float, 'label': str}
                },
                'summary': {
                    'has_depression': bool,
                    'has_anxiety': bool,
                    'conditions_detected': List[str]
                }
            }

            Para modelo binario (retrocompatibilidad):
            {
                'text': str,
                'prediction': int,
                'label': str,
                'probability': float,
                'confidence': float
            }
        """
        if not text or not text.strip():
            raise ValueError("El texto no puede estar vacío")

        # 1. Limpiar texto si es necesario
        processed_text = clean_text(text) if clean_input else text

        # 2. Generar embedding BERT
        embedding = self.encoder.encode_texts(
            [processed_text],
            show_progress=False
        )

        # 3. Predecir según tipo de modelo
        if self.is_multi_label:
            return self._predict_multi_label(text, embedding, return_probabilities)
        else:
            return self._predict_binary(text, embedding, return_probabilities)

    def _predict_binary(
        self,
        text: str,
        embedding: np.ndarray,
        return_probabilities: bool
    ) -> Dict:
        """Predicción para modelo binario (solo depresión)."""
        prediction = self.classifier.predict(embedding)[0]
        probabilities = self.classifier.predict_proba(embedding)[0]
        prob_depression = probabilities[1]
        confidence = max(probabilities)
        threshold = self.thresholds['depression']
        has_depression = prob_depression >= threshold

        result = {
            'text': text,
            'prediction': int(has_depression),
            'label': 'Depresión' if has_depression else 'Sin depresión',
            'raw_prediction': int(prediction),
            'threshold': float(threshold)
        }

        if return_probabilities:
            result['probability'] = float(prob_depression)
            result['confidence'] = float(confidence)

        return result

    def _predict_multi_label(
        self,
        text: str,
        embedding: np.ndarray,
        return_probabilities: bool
    ) -> Dict:
        """Predicción para modelo multi-etiqueta (depresión + ansiedad)."""
        # Obtener predicciones y probabilidades
        raw_predictions = self.classifier.predict(embedding)[0]  # [dep, anx]
        probas = self.classifier.predict_proba(embedding)

        # Extraer probabilidades para cada etiqueta
        prob_depression = probas[0][0, 1]  # P(depression=1)
        prob_anxiety = probas[1][0, 1]      # P(anxiety=1)
        depression_threshold = self.thresholds['depression']
        anxiety_threshold = self.thresholds['anxiety']
        has_depression = prob_depression >= depression_threshold
        has_anxiety = prob_anxiety >= anxiety_threshold

        # Construir resultado estructurado
        result = {
            'text': text,
            'predictions': {
                'depression': {
                    'prediction': int(has_depression),
                    'label': 'Depresión' if has_depression else 'Sin depresión',
                    'raw_prediction': int(raw_predictions[0]),
                    'threshold': float(depression_threshold)
                },
                'anxiety': {
                    'prediction': int(has_anxiety),
                    'label': 'Ansiedad' if has_anxiety else 'Sin ansiedad',
                    'raw_prediction': int(raw_predictions[1]),
                    'threshold': float(anxiety_threshold)
                }
            },
            'summary': {
                'has_depression': bool(has_depression),
                'has_anxiety': bool(has_anxiety),
                'conditions_detected': []
            }
        }

        # Agregar condiciones detectadas
        if has_depression:
            result['summary']['conditions_detected'].append('depression')
        if has_anxiety:
            result['summary']['conditions_detected'].append('anxiety')

        # Agregar probabilidades si se solicitan
        if return_probabilities:
            result['predictions']['depression']['probability'] = float(prob_depression)
            result['predictions']['depression']['confidence'] = float(max(probas[0][0]))
            result['predictions']['anxiety']['probability'] = float(prob_anxiety)
            result['predictions']['anxiety']['confidence'] = float(max(probas[1][0]))

        return result

    def predict_batch(
        self,
        texts: List[str],
        return_probabilities: bool = True,
        clean_input: bool = True,
        show_progress: bool = True
    ) -> List[Dict]:
        """
        Predice trastornos mentales para múltiples textos.

        Args:
            texts: Lista de textos a analizar
            return_probabilities: Incluir probabilidades en las respuestas
            clean_input: Aplicar limpieza de texto antes de predecir
            show_progress: Mostrar barra de progreso

        Returns:
            Lista de diccionarios con predicciones
        """
        if not texts:
            return []

        # 1. Limpiar textos si es necesario
        processed_texts = [clean_text(t) if clean_input else t for t in texts]

        # 2. Generar embeddings BERT (batch processing eficiente)
        embeddings = self.encoder.encode_texts(
            processed_texts,
            show_progress=show_progress
        )

        # 3. Predecir según tipo de modelo
        if self.is_multi_label:
            return self._predict_batch_multi_label(texts, embeddings, return_probabilities)
        else:
            return self._predict_batch_binary(texts, embeddings, return_probabilities)

    def _predict_batch_binary(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        return_probabilities: bool
    ) -> List[Dict]:
        """Predicción batch para modelo binario."""
        predictions = self.classifier.predict(embeddings)
        probabilities = self.classifier.predict_proba(embeddings)

        results = []
        for i, text in enumerate(texts):
            prediction = predictions[i]
            probs = probabilities[i]
            prob_depression = probs[1]
            confidence = max(probs)
            threshold = self.thresholds['depression']
            has_depression = prob_depression >= threshold

            result = {
                'text': text,
                'prediction': int(has_depression),
                'label': 'Depresión' if has_depression else 'Sin depresión',
                'raw_prediction': int(prediction),
                'threshold': float(threshold)
            }

            if return_probabilities:
                result['probability'] = float(prob_depression)
                result['confidence'] = float(confidence)

            results.append(result)

        return results

    def _predict_batch_multi_label(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        return_probabilities: bool
    ) -> List[Dict]:
        """Predicción batch para modelo multi-etiqueta."""
        predictions = self.classifier.predict(embeddings)  # (N, 2)
        probas = self.classifier.predict_proba(embeddings)  # List of 2 arrays

        results = []
        for i, text in enumerate(texts):
            pred = predictions[i]  # [dep, anx]
            prob_depression = probas[0][i, 1]
            prob_anxiety = probas[1][i, 1]
            depression_threshold = self.thresholds['depression']
            anxiety_threshold = self.thresholds['anxiety']
            has_depression = prob_depression >= depression_threshold
            has_anxiety = prob_anxiety >= anxiety_threshold

            result = {
                'text': text,
                'predictions': {
                    'depression': {
                        'prediction': int(has_depression),
                        'label': 'Depresión' if has_depression else 'Sin depresión',
                        'raw_prediction': int(pred[0]),
                        'threshold': float(depression_threshold)
                    },
                    'anxiety': {
                        'prediction': int(has_anxiety),
                        'label': 'Ansiedad' if has_anxiety else 'Sin ansiedad',
                        'raw_prediction': int(pred[1]),
                        'threshold': float(anxiety_threshold)
                    }
                },
                'summary': {
                    'has_depression': bool(has_depression),
                    'has_anxiety': bool(has_anxiety),
                    'conditions_detected': []
                }
            }

            if has_depression:
                result['summary']['conditions_detected'].append('depression')
            if has_anxiety:
                result['summary']['conditions_detected'].append('anxiety')

            if return_probabilities:
                result['predictions']['depression']['probability'] = float(prob_depression)
                result['predictions']['depression']['confidence'] = float(max(probas[0][i]))
                result['predictions']['anxiety']['probability'] = float(prob_anxiety)
                result['predictions']['anxiety']['confidence'] = float(max(probas[1][i]))

            results.append(result)

        return results

    def get_model_info(self) -> Dict:
        """
        Obtiene información del modelo cargado.

        Returns:
            Diccionario con metadata del modelo
        """
        info = {
            'model_name': self.model_name,
            'model_type': 'multi_label' if self.is_multi_label else 'binary',
            'labels': self.labels,
            'metadata_available': self.metadata is not None
        }

        if self.metadata:
            info['bert_model'] = self.metadata.get('bert_model')
            info['created_at'] = self.metadata.get('created_at')
            info['metrics'] = self.metadata.get('metrics')
            info['xgboost_params'] = self.metadata.get('xgboost_params')

        info['decision_thresholds'] = self.thresholds

        return info

    def is_multilabel_model(self) -> bool:
        """Retorna True si el modelo cargado es multi-etiqueta."""
        return self.is_multi_label


if __name__ == "__main__":
    # Ejemplo de uso
    print("=" * 80)
    print("🧪 EJEMPLO DE USO - PREDICTION PIPELINE")
    print("=" * 80)

    # Inicializar pipeline
    pipeline = PredictionPipeline()

    # Mostrar info del modelo
    print(f"\n📋 Modelo cargado:")
    print(f"   Tipo: {'Multi-Etiqueta' if pipeline.is_multi_label else 'Binario'}")
    print(f"   Etiquetas: {pipeline.labels}")

    # Ejemplo de predicción
    print("\n📝 Ejemplo de predicción:")
    print("-" * 80)

    text = "Me siento muy triste, ansioso y sin energía para hacer nada"
    result = pipeline.predict_text(text)

    print(f"\nTexto: {text}")

    if pipeline.is_multi_label:
        print(f"\nResultados Multi-Etiqueta:")
        for condition, pred in result['predictions'].items():
            print(f"   📌 {condition.upper()}:")
            print(f"      • Predicción: {pred['label']}")
            print(f"      • Probabilidad: {pred.get('probability', 'N/A'):.2%}")

        print(f"\n   Condiciones detectadas: {result['summary']['conditions_detected']}")
    else:
        print(f"\nPredicción: {result['label']}")
        print(f"Probabilidad: {result.get('probability', 'N/A'):.2%}")

    print("\n" + "=" * 80)
    print("✅ Pipeline funcionando correctamente!")
    print("=" * 80)
