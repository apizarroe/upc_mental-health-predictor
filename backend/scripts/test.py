#!/usr/bin/env python3
"""
Script CLI para validar/testear el modelo BERT + XGBoost entrenado.
Permite evaluar conversaciones específicas del dataset y verificar predicciones.

Uso:
    # Validar con conversaciones aleatorias del dataset
    python scripts/test.py

    # Validar conversaciones específicas por índice
    python scripts/test.py --indices 0 5 10 15

    # Validar con texto personalizado
    python scripts/test.py --text "Me siento muy triste últimamente y sin energía"

    # Evaluar todo el dataset de prueba
    python scripts/test.py --full-test

    # Usar modelo específico
    python scripts/test.py --model-path data/trained_models/depression_bert_xgboost_20241118.pkl
"""

# IMPORTANTE: Configurar variables de entorno ANTES de cualquier import
# Fix para macOS: Prevenir crash por conflicto entre libiomp5 y libomp
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '4'
os.environ['MKL_NUM_THREADS'] = '4'

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pandas as pd
import numpy as np
from app.ml.prediction_pipeline import PredictionPipeline
from app.ml.preprocessor import TextPreprocessor
from app.ml.data_loaders import ParquetChatLoader, CSVPatientLoader
from app.ml.text_processing import clean_text


class ModelTester:
    """Clase para validar y testear el modelo entrenado."""

    def __init__(
        self,
        model_path: str = None,
        data_path: str = "data/datasets/train-00000-of-00001.parquet"
    ):
        """
        Inicializa el tester con el modelo y datos.

        Args:
            model_path: Ruta al modelo entrenado (.pkl)
            data_path: Ruta al dataset parquet
        """
        self.data_path = Path(data_path)
        self.preprocessor = TextPreprocessor()

        # Usar PredictionPipeline para todas las predicciones
        self.pipeline = PredictionPipeline(model_path=model_path, verbose=True)

    def load_dataset(self) -> pd.DataFrame:
        """Carga el dataset de conversaciones."""
        if not self.data_path.exists():
            print(f"❌ No se encontró el dataset: {self.data_path}")
            sys.exit(1)

        df = pd.read_parquet(self.data_path)
        print(f"✅ Dataset cargado: {len(df)} conversaciones")
        return df

    def extract_conversation_text(self, conversation: List[Dict]) -> str:
        """
        Extrae y formatea el texto de una conversación para análisis.

        Args:
            conversation: Lista de mensajes de la conversación

        Returns:
            Texto extraído y limpiado
        """
        # Extraer solo mensajes del usuario
        user_text = self.preprocessor.extract_user_messages(conversation)
        # Limpiar texto
        cleaned_text = self.preprocessor.clean_text(user_text)
        return cleaned_text

    def predict_conversation(
        self,
        conversation_text: str,
        show_details: bool = True
    ) -> Tuple[int, float, Dict]:
        """
        Predice si una conversación indica depresión.

        Args:
            conversation_text: Texto de la conversación
            show_details: Mostrar detalles de la predicción

        Returns:
            Tupla de (predicción, probabilidad, detalles)
        """
        # Usar PredictionPipeline para predecir (ya incluye limpieza de texto)
        result = self.pipeline.predict_text(
            conversation_text,
            return_probabilities=True,
            clean_input=False  # Ya viene limpio del preprocessor
        )

        # Convertir formato del pipeline al formato esperado por el tester
        details = {
            'prediction': result['prediction'],
            'probability_no_depression': 1.0 - result['probability'],
            'probability_depression': result['probability'],
            'confidence': result['confidence'],
            'text_length': len(conversation_text),
            'has_depression': result['prediction'] == 1
        }

        if show_details:
            self._print_prediction(conversation_text, details)

        return result['prediction'], result['probability'], details

    def _print_prediction(self, text: str, details: Dict):
        """Imprime los detalles de una predicción."""
        print("\n" + "=" * 80)
        print("📝 ANÁLISIS DE CONVERSACIÓN")
        print("=" * 80)

        # Mostrar extracto del texto
        max_preview = 200
        text_preview = text[:max_preview] + "..." if len(text) > max_preview else text
        print(f"\n💬 Texto analizado ({len(text)} caracteres):")
        print(f"   {text_preview}")

        # Resultado
        result = "DEPRESIÓN DETECTADA ⚠️" if details['has_depression'] else "SIN INDICADORES ✅"
        print(f"\n🎯 Resultado: {result}")

        # Probabilidades
        print(f"\n📊 Probabilidades:")
        print(f"   • Sin depresión: {details['probability_no_depression']:.2%}")
        print(f"   • Con depresión: {details['probability_depression']:.2%}")
        print(f"   • Confianza:     {details['confidence']:.2%}")

    def test_random_conversations(self, n_samples: int = 5):
        """
        Testea conversaciones aleatorias del dataset.

        Args:
            n_samples: Número de conversaciones a testear
        """
        print(f"\n🎲 Testeando {n_samples} conversaciones aleatorias...\n")

        df = self.load_dataset()

        # Seleccionar muestras aleatorias
        sample_df = df.sample(n=min(n_samples, len(df)), random_state=42)

        results = []

        for idx, (_, row) in enumerate(sample_df.iterrows(), 1):
            print(f"\n{'='*80}")
            print(f"CONVERSACIÓN #{idx}")
            print(f"{'='*80}")

            conversation = row['chat']
            text = self.extract_conversation_text(conversation)

            # Predicción real del modelo
            prediction, prob, details = self.predict_conversation(text, show_details=True)

            # Etiqueta heurística (para comparación)
            heuristic_label = self.preprocessor.detect_depression_indicators(text)

            print(f"\n🔍 Comparación:")
            print(f"   • Modelo predice:     {'Depresión' if prediction == 1 else 'Sin depresión'}")
            print(f"   • Heurística detecta: {'Depresión' if heuristic_label == 1 else 'Sin depresión'}")
            print(f"   • Coinciden:          {'✅ Sí' if prediction == heuristic_label else '❌ No'}")

            results.append({
                'index': idx,
                'prediction': prediction,
                'probability': prob,
                'heuristic': heuristic_label,
                'match': prediction == heuristic_label
            })

        # Resumen
        self._print_summary(results)

    def test_specific_indices(self, indices: List[int]):
        """
        Testea conversaciones específicas por índice.

        Args:
            indices: Lista de índices a testear
        """
        print(f"\n🔍 Testeando conversaciones en índices: {indices}\n")

        df = self.load_dataset()

        results = []

        for idx in indices:
            if idx >= len(df):
                print(f"⚠️  Índice {idx} fuera de rango (dataset tiene {len(df)} conversaciones)")
                continue

            print(f"\n{'='*80}")
            print(f"CONVERSACIÓN EN ÍNDICE #{idx}")
            print(f"{'='*80}")

            conversation = df.iloc[idx]['chat']
            text = self.extract_conversation_text(conversation)

            prediction, prob, details = self.predict_conversation(text, show_details=True)
            heuristic_label = self.preprocessor.detect_depression_indicators(text)

            print(f"\n🔍 Comparación:")
            print(f"   • Modelo predice:     {'Depresión' if prediction == 1 else 'Sin depresión'}")
            print(f"   • Heurística detecta: {'Depresión' if heuristic_label == 1 else 'Sin depresión'}")

            results.append({
                'index': idx,
                'prediction': prediction,
                'probability': prob,
                'heuristic': heuristic_label,
                'match': prediction == heuristic_label
            })

        self._print_summary(results)

    def test_custom_text(self, text: str):
        """
        Testea un texto personalizado.

        Args:
            text: Texto a analizar
        """
        print("\n🎯 Testeando texto personalizado...")

        cleaned_text = self.preprocessor.clean_text(text)
        prediction, prob, details = self.predict_conversation(cleaned_text, show_details=True)

    def test_full_dataset(self):
        """Evalúa el modelo en todo el dataset."""
        print("\n📊 Evaluando modelo en dataset completo...\n")

        df = self.load_dataset()

        texts = []
        labels = []
        predictions = []
        probabilities = []

        print("🔄 Procesando conversaciones...")

        for idx, row in df.iterrows():
            conversation = row['chat']
            text = self.extract_conversation_text(conversation)

            # Etiqueta heurística
            label = self.preprocessor.detect_depression_indicators(text)

            # Predicción del modelo
            embedding = self.encoder.encode_texts([text])
            pred = self.classifier.predict(embedding)[0]
            prob = self.classifier.predict_proba(embedding)[0][1]

            texts.append(text)
            labels.append(label)
            predictions.append(pred)
            probabilities.append(prob)

            if (idx + 1) % 100 == 0:
                print(f"   Procesadas {idx + 1}/{len(df)} conversaciones...")

        # Convertir a numpy arrays
        y_true = np.array(labels)
        y_pred = np.array(predictions)

        # Calcular métricas
        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
            confusion_matrix,
            classification_report
        )

        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        cm = confusion_matrix(y_true, y_pred)

        print("\n" + "=" * 80)
        print("📊 EVALUACIÓN COMPLETA DEL DATASET")
        print("=" * 80)

        print(f"\n📈 Métricas generales:")
        print(f"   • Total de conversaciones: {len(df)}")
        print(f"   • Accuracy:  {accuracy:.4f} ({accuracy:.2%})")
        print(f"   • Precision: {precision:.4f} ({precision:.2%})")
        print(f"   • Recall:    {recall:.4f} ({recall:.2%})")
        print(f"   • F1-Score:  {f1:.4f} ({f1:.2%})")

        print(f"\n📋 Matriz de Confusión:")
        print(f"   {'':>15} Predicho: No    Predicho: Sí")
        print(f"   Real: No      {cm[0][0]:>8}      {cm[0][1]:>8}")
        print(f"   Real: Sí      {cm[1][0]:>8}      {cm[1][1]:>8}")

        print(f"\n📊 Reporte de Clasificación:")
        print(classification_report(
            y_true,
            y_pred,
            target_names=['Sin Depresión', 'Con Depresión']
        ))

        # Análisis de errores
        false_positives = np.sum((y_pred == 1) & (y_true == 0))
        false_negatives = np.sum((y_pred == 0) & (y_true == 1))

        print(f"\n⚠️  Análisis de errores:")
        print(f"   • Falsos positivos: {false_positives} (modelo predice depresión pero no hay)")
        print(f"   • Falsos negativos: {false_negatives} (modelo NO predice depresión pero sí hay)")

    def _print_summary(self, results: List[Dict]):
        """Imprime resumen de resultados."""
        if not results:
            return

        print("\n" + "=" * 80)
        print("📊 RESUMEN DE RESULTADOS")
        print("=" * 80)

        total = len(results)
        with_depression = sum(1 for r in results if r['prediction'] == 1)
        without_depression = total - with_depression
        matches = sum(1 for r in results if r['match'])
        avg_prob = np.mean([r['probability'] for r in results])

        print(f"\n📈 Estadísticas:")
        print(f"   • Total analizado:      {total}")
        print(f"   • Con depresión:        {with_depression} ({with_depression/total:.1%})")
        print(f"   • Sin depresión:        {without_depression} ({without_depression/total:.1%})")
        print(f"   • Coinciden heurística: {matches} ({matches/total:.1%})")
        print(f"   • Prob. promedio:       {avg_prob:.2%}")

    def test_csv_file(self, csv_path: str):
        """Testea datos desde un archivo CSV."""
        print(f"\n📂 Testeando archivo CSV: {csv_path}\n")

        # Cargar usando CSVPatientLoader
        loader = CSVPatientLoader(file_path=csv_path, session_column='sesion')
        texts = loader.load_grouped_by_session()

        results = []

        for idx, text in enumerate(texts, 1):
            print(f"\n{'='*80}")
            print(f"SESIÓN #{idx}")
            print(f"{'='*80}")

            # Limpiar texto
            clean_text_str = clean_text(text)

            # Predicción del modelo
            prediction, prob, details = self.predict_conversation(clean_text_str, show_details=True)

            # Etiqueta heurística (para comparación)
            heuristic_label = self.preprocessor.detect_depression_indicators(clean_text_str)

            print(f"\n🔍 Comparación:")
            print(f"   • Modelo predice:     {'Depresión' if prediction == 1 else 'Sin depresión'}")
            print(f"   • Heurística detecta: {'Depresión' if heuristic_label == 1 else 'Sin depresión'}")
            print(f"   • Coinciden:          {'✅ Sí' if prediction == heuristic_label else '❌ No'}")

            results.append({
                'index': idx,
                'prediction': prediction,
                'probability': prob,
                'heuristic': heuristic_label,
                'match': prediction == heuristic_label
            })

        # Resumen
        self._print_summary(results)


def parse_args():
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Validar/testear modelo BERT + XGBoost entrenado',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

    # Validar conversaciones aleatorias (default: 5)
    python test_model.py

    # Validar 10 conversaciones aleatorias
    python test_model.py --random 10

    # Validar conversaciones específicas
    python test_model.py --indices 0 5 10 15 20

    # Testear texto personalizado
    python test_model.py --text "Me siento muy triste y sin energía"

    # Evaluación completa del dataset
    python test_model.py --full-test

    # Usar modelo específico
    python test_model.py --model-path data/trained_models/depression_bert_xgboost_20241118.pkl
        """
    )

    parser.add_argument(
        '--model-path',
        type=str,
        default=None,
        help='Ruta al modelo entrenado (.pkl). Si no se especifica, usa el más reciente'
    )

    parser.add_argument(
        '--data-path',
        type=str,
        default='data/datasets/train-00000-of-00001.parquet',
        help='Ruta al dataset parquet'
    )

    parser.add_argument(
        '--random',
        type=int,
        default=None,
        help='Número de conversaciones aleatorias a testear'
    )

    parser.add_argument(
        '--indices',
        type=int,
        nargs='+',
        help='Índices específicos de conversaciones a testear'
    )

    parser.add_argument(
        '--text',
        type=str,
        help='Texto personalizado para analizar'
    )

    parser.add_argument(
        '--full-test',
        action='store_true',
        help='Evaluar modelo en todo el dataset'
    )

    parser.add_argument(
        '--csv',
        action='store_true',
        help='Indica que el data-path es un archivo CSV (default: Parquet)'
    )

    return parser.parse_args()


def main():
    """Función principal."""
    args = parse_args()

    print("🧠 VALIDACIÓN DE MODELO BERT + XGBOOST")
    print("=" * 80)

    try:
        # Inicializar tester
        tester = ModelTester(
            model_path=args.model_path,
            data_path=args.data_path
        )

        # Ejecutar según argumentos
        if args.csv:
            tester.test_csv_file(args.data_path)

        elif args.full_test:
            tester.test_full_dataset()

        elif args.text:
            tester.test_custom_text(args.text)

        elif args.indices:
            tester.test_specific_indices(args.indices)

        elif args.random:
            tester.test_random_conversations(args.random)

        else:
            # Default: 5 conversaciones aleatorias
            tester.test_random_conversations(5)

        print("\n✅ Validación completada!\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Validación interrumpida por el usuario")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error durante la validación: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
