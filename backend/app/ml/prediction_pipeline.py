"""
Pipeline completo de predicción: BERT + XGBoost
para detección de depresión en producción.
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import sys

from .bert_encoder import BERTEncoder
from .classifier import DepressionClassifier
from .text_processing import clean_text


class PredictionPipeline:
    """
    Pipeline completo para predicción con modelo entrenado.

    Encapsula toda la lógica necesaria para:
    1. Cargar modelo entrenado (.pkl) y metadata (.json)
    2. Inicializar BERT encoder con la configuración correcta
    3. Preprocesar textos
    4. Generar embeddings BERT
    5. Clasificar con XGBoost
    6. Retornar predicciones y probabilidades

    Uso:
        # Con modelo por defecto (el más reciente)
        pipeline = PredictionPipeline()
        result = pipeline.predict_text("Me siento muy triste últimamente")

        # Con modelo específico
        pipeline = PredictionPipeline(model_path="data/trained_models/mi_modelo.pkl")
        result = pipeline.predict_text("Texto a analizar")

        # Batch prediction
        results = pipeline.predict_batch(["texto1", "texto2", "texto3"])
    """

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
        self.encoder: Optional[BERTEncoder] = None
        self.classifier = DepressionClassifier()

        # Metadata del modelo
        self.metadata: Optional[Dict] = None
        self.model_name: Optional[str] = None

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

        # Buscar archivos .pkl
        model_files = list(self.models_dir.glob("depression_bert_xgboost_*.pkl"))

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

        # Cargar clasificador XGBoost
        self.classifier.load(str(model_file))
        self.model_name = model_file.stem

        # Cargar metadata para obtener configuración BERT
        metadata_file = model_file.parent / f"{model_file.stem}_metadata.json"

        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)

            bert_model = self.metadata.get('bert_model', 'dccuchile/bert-base-spanish-wwm-cased')
            max_length = self.metadata.get('max_length', 512)

            if self.verbose:
                print(f"\n📋 Configuración del modelo:")
                print(f"   • Nombre: {self.model_name}")
                print(f"   • BERT model: {bert_model}")
                print(f"   • Max length: {max_length}")
                print(f"   • Entrenado: {self.metadata.get('created_at', 'N/A')}")

                # Mostrar métricas si existen
                if 'metrics' in self.metadata and 'test' in self.metadata['metrics']:
                    test_metrics = self.metadata['metrics']['test']
                    print(f"\n📊 Métricas del modelo (Test Set):")
                    print(f"   • Accuracy:  {test_metrics.get('accuracy', 'N/A'):.4f}")
                    print(f"   • Precision: {test_metrics.get('precision', 'N/A'):.4f}")
                    print(f"   • Recall:    {test_metrics.get('recall', 'N/A'):.4f}")
                    print(f"   • F1-Score:  {test_metrics.get('f1_score', 'N/A'):.4f}")

            # Inicializar encoder BERT con la configuración del modelo
            self.encoder = BERTEncoder(
                model_name=bert_model,
                max_length=max_length,
                batch_size=16  # Para predicción usamos batch pequeño
            )
        else:
            if self.verbose:
                print("⚠️  No se encontró archivo de metadata, usando configuración default")

            # Usar configuración por defecto
            self.encoder = BERTEncoder()

        if self.verbose:
            print("\n✅ Pipeline de predicción listo!")

    def predict_text(
        self,
        text: str,
        return_probabilities: bool = True,
        clean_input: bool = True
    ) -> Dict:
        """
        Predice depresión para un texto dado.

        Args:
            text: Texto a analizar
            return_probabilities: Incluir probabilidades en la respuesta
            clean_input: Aplicar limpieza de texto antes de predecir

        Returns:
            Diccionario con predicción y detalles:
            {
                'text': str,              # Texto original
                'prediction': int,        # 0 = sin depresión, 1 = con depresión
                'label': str,             # "Depresión" o "Sin depresión"
                'probability': float,     # Probabilidad de depresión (0-1)
                'confidence': float       # Confianza de la predicción
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

        # 3. Predecir con XGBoost
        prediction = self.classifier.predict(embedding)[0]

        # 4. Obtener probabilidades
        probabilities = self.classifier.predict_proba(embedding)[0]
        prob_depression = probabilities[1]  # Probabilidad de clase 1 (depresión)

        # 5. Calcular confianza (qué tan seguro está el modelo)
        confidence = max(probabilities)

        # 6. Crear resultado
        result = {
            'text': text,
            'prediction': int(prediction),
            'label': 'Depresión' if prediction == 1 else 'Sin depresión'
        }

        if return_probabilities:
            result['probability'] = float(prob_depression)
            result['confidence'] = float(confidence)

        return result

    def predict_batch(
        self,
        texts: List[str],
        return_probabilities: bool = True,
        clean_input: bool = True,
        show_progress: bool = True
    ) -> List[Dict]:
        """
        Predice depresión para múltiples textos de forma eficiente.

        Args:
            texts: Lista de textos a analizar
            return_probabilities: Incluir probabilidades en las respuestas
            clean_input: Aplicar limpieza de texto antes de predecir
            show_progress: Mostrar barra de progreso

        Returns:
            Lista de diccionarios con predicciones (mismo formato que predict_text)
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

        # 3. Predecir con XGBoost (muy rápido para batch)
        predictions = self.classifier.predict(embeddings)
        probabilities = self.classifier.predict_proba(embeddings)

        # 4. Crear resultados
        results = []
        for i, text in enumerate(texts):
            prediction = predictions[i]
            probs = probabilities[i]
            prob_depression = probs[1]
            confidence = max(probs)

            result = {
                'text': text,
                'prediction': int(prediction),
                'label': 'Depresión' if prediction == 1 else 'Sin depresión'
            }

            if return_probabilities:
                result['probability'] = float(prob_depression)
                result['confidence'] = float(confidence)

            results.append(result)

        return results

    def get_model_info(self) -> Dict:
        """
        Obtiene información del modelo cargado.

        Returns:
            Diccionario con metadata del modelo
        """
        if self.metadata:
            return {
                'model_name': self.model_name,
                'bert_model': self.metadata.get('bert_model'),
                'created_at': self.metadata.get('created_at'),
                'metrics': self.metadata.get('metrics'),
                'xgboost_params': self.metadata.get('xgboost_params')
            }
        else:
            return {
                'model_name': self.model_name,
                'metadata_available': False
            }


if __name__ == "__main__":
    # Ejemplo de uso
    print("=" * 80)
    print("🧪 EJEMPLO DE USO - PREDICTION PIPELINE")
    print("=" * 80)

    # Inicializar pipeline
    pipeline = PredictionPipeline()

    # Ejemplo 1: Predicción individual
    print("\n📝 Ejemplo 1: Predicción individual")
    print("-" * 80)

    text = "Últimamente me he sentido muy triste y sin energía para hacer nada"
    result = pipeline.predict_text(text)

    print(f"\nTexto: {result['text']}")
    print(f"Predicción: {result['label']}")
    print(f"Probabilidad de depresión: {result['probability']:.2%}")
    print(f"Confianza: {result['confidence']:.2%}")

    # Ejemplo 2: Batch prediction
    print("\n\n📝 Ejemplo 2: Predicción en batch")
    print("-" * 80)

    texts = [
        "Me siento muy deprimido y sin esperanza",
        "Hoy fue un día excelente, logré todos mis objetivos",
        "No puedo dormir y no tengo apetito"
    ]

    results = pipeline.predict_batch(texts, show_progress=False)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['text'][:50]}...")
        print(f"   → {result['label']} ({result['probability']:.2%})")

    print("\n" + "=" * 80)
    print("✅ Pipeline funcionando correctamente!")
    print("=" * 80)
