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

    # Evaluar todo el dataset (multi-label: depresión + ansiedad)
    python scripts/test.py --full-test

    # Evaluar todo el dataset solo para depresión
    python scripts/test.py --full-test --condition depression

    # Evaluar todo el dataset solo para ansiedad
    python scripts/test.py --full-test --condition anxiety

    # Usar modelo específico
    python scripts/test.py --model-path data/trained_models/mental_health_multilabel_20241118.pkl
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
# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pandas as pd
import numpy as np
from app.ml.prediction_pipeline import PredictionPipeline
from app.ml.preprocessor import TextPreprocessor
from app.ml.data_loaders import CSVPatientLoader
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
        Predice si una conversación indica depresión y/o ansiedad.

        Args:
            conversation_text: Texto de la conversación
            show_details: Mostrar detalles de la predicción

        Returns:
            Tupla de (predicción_depresión, probabilidad_depresión, detalles)
        """
        # Usar PredictionPipeline para predecir (ya incluye limpieza de texto)
        result = self.pipeline.predict_text(
            conversation_text,
            return_probabilities=True,
            clean_input=False  # Ya viene limpio del preprocessor
        )

        # Verificar si es modelo multi-etiqueta o binario
        if self.pipeline.is_multi_label:
            # Formato multi-etiqueta
            dep_pred = result['predictions']['depression']
            anx_pred = result['predictions']['anxiety']

            details = {
                'prediction': dep_pred['prediction'],
                'probability_no_depression': 1.0 - dep_pred.get('probability', 0),
                'probability_depression': dep_pred.get('probability', 0),
                'confidence': dep_pred.get('confidence', 0),
                'text_length': len(conversation_text),
                'has_depression': dep_pred['prediction'] == 1,
                # Campos adicionales para ansiedad
                'has_anxiety': anx_pred['prediction'] == 1,
                'probability_anxiety': anx_pred.get('probability', 0),
                'anxiety_confidence': anx_pred.get('confidence', 0),
                'conditions_detected': result['summary']['conditions_detected']
            }

            if show_details:
                self._print_multilabel_prediction(conversation_text, details)

            return dep_pred['prediction'], dep_pred.get('probability', 0), details
        else:
            # Formato binario (retrocompatibilidad)
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

    def _print_multilabel_prediction(self, text: str, details: Dict):
        """Imprime los detalles de una predicción multi-etiqueta."""
        print("\n" + "=" * 80)
        print("📝 ANÁLISIS DE CONVERSACIÓN (Multi-Etiqueta)")
        print("=" * 80)

        # Mostrar extracto del texto
        max_preview = 200
        text_preview = text[:max_preview] + "..." if len(text) > max_preview else text
        print(f"\n💬 Texto analizado ({len(text)} caracteres):")
        print(f"   {text_preview}")

        # Resultado general
        conditions = details.get('conditions_detected', [])
        if conditions:
            result = f"DETECTADO: {', '.join(conditions).upper()} ⚠️"
        else:
            result = "SIN INDICADORES SIGNIFICATIVOS ✅"
        print(f"\n🎯 Resultado: {result}")

        # Depresión
        dep_status = "⚠️ DETECTADA" if details['has_depression'] else "✅ No detectada"
        print(f"\n📊 DEPRESIÓN: {dep_status}")
        print(f"   • Probabilidad: {details['probability_depression']:.2%}")
        print(f"   • Confianza:    {details['confidence']:.2%}")

        # Ansiedad
        anx_status = "⚠️ DETECTADA" if details.get('has_anxiety', False) else "✅ No detectada"
        print(f"\n📊 ANSIEDAD: {anx_status}")
        print(f"   • Probabilidad: {details.get('probability_anxiety', 0):.2%}")
        print(f"   • Confianza:    {details.get('anxiety_confidence', 0):.2%}")

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

    def test_full_dataset(self, conditions: List[str] = None):
        """
        Evalúa el modelo en todo el dataset.

        Args:
            conditions: Lista de condiciones a evaluar.
                       - None o ['all']: Evalúa todas (multi-label)
                       - ['depression']: Solo depresión
                       - ['anxiety']: Solo ansiedad
                       - ['depression', 'anxiety']: Ambas por separado
                       Escalable para agregar más trastornos a futuro.
        """
        # Mapeo de condiciones disponibles (escalable)
        available_conditions = {
            'depression': {
                'name': 'Depresión',
                'heuristic_method': self.preprocessor.detect_depression_indicators,
                'keywords': self.preprocessor.depression_keywords
            },
            'anxiety': {
                'name': 'Ansiedad',
                'heuristic_method': self.preprocessor.detect_anxiety_indicators,
                'keywords': self.preprocessor.anxiety_keywords
            }
            # Agregar más trastornos aquí en el futuro:
            # 'ptsd': {...}, 'bipolar': {...}, etc.
        }

        # Determinar condiciones a evaluar
        if conditions is None or 'all' in conditions:
            conditions_to_eval = list(available_conditions.keys())
            mode = "MULTI-ETIQUETA"
        else:
            conditions_to_eval = [c for c in conditions if c in available_conditions]
            if not conditions_to_eval:
                print(f"❌ Condiciones no válidas. Disponibles: {list(available_conditions.keys())}")
                return
            mode = "ESPECÍFICO" if len(conditions_to_eval) == 1 else "MULTI-ETIQUETA"

        print(f"\n📊 Evaluando modelo ({mode}) en dataset completo...")
        print(f"   Condiciones: {', '.join(conditions_to_eval)}\n")

        df = self.load_dataset()

        # Almacenar datos por condición
        data_by_condition = {cond: {'labels': [], 'predictions': []} for cond in conditions_to_eval}

        print("🔄 Procesando conversaciones...")

        for idx, row in df.iterrows():
            conversation = row['chat']
            text = self.extract_conversation_text(conversation)

            # Predicción del modelo
            result = self.pipeline.predict_text(text, return_probabilities=True, clean_input=False)

            # Procesar cada condición
            for cond in conditions_to_eval:
                # Etiqueta heurística
                heuristic_label = available_conditions[cond]['heuristic_method'](text)
                data_by_condition[cond]['labels'].append(heuristic_label)

                # Predicción del modelo para esta condición
                pred = result['predictions'][cond]['prediction']
                data_by_condition[cond]['predictions'].append(pred)

            if (idx + 1) % 100 == 0:
                print(f"   Procesadas {idx + 1}/{len(df)} conversaciones...")

        # Importar métricas
        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
            confusion_matrix
        )

        print("\n" + "=" * 80)
        print(f"📊 EVALUACIÓN {mode} COMPLETA")
        print("=" * 80)
        print(f"\n   • Total de conversaciones: {len(df)}")

        # Métricas por condición
        metrics_by_condition = {}
        for cond in conditions_to_eval:
            y_true = np.array(data_by_condition[cond]['labels'])
            y_pred = np.array(data_by_condition[cond]['predictions'])

            acc = accuracy_score(y_true, y_pred)
            prec = precision_score(y_true, y_pred, zero_division=0)
            rec = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
            cm = confusion_matrix(y_true, y_pred)

            metrics_by_condition[cond] = {
                'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1,
                'confusion_matrix': cm, 'y_true': y_true, 'y_pred': y_pred
            }

            cond_name = available_conditions[cond]['name']
            print(f"\n{'-' * 40}")
            print(f"📌 {cond_name.upper()}")
            print(f"{'-' * 40}")
            print(f"   • Accuracy:  {acc:.4f} ({acc:.2%})")
            print(f"   • Precision: {prec:.4f} ({prec:.2%})")
            print(f"   • Recall:    {rec:.4f} ({rec:.2%})")
            print(f"   • F1-Score:  {f1:.4f} ({f1:.2%})")

            print(f"\n   Matriz de Confusión:")
            print(f"   {'':>15} Predicho: No    Predicho: Sí")
            if len(cm) == 2:
                print(f"   Real: No      {cm[0][0]:>8}      {cm[0][1]:>8}")
                print(f"   Real: Sí      {cm[1][0]:>8}      {cm[1][1]:>8}")

                fp = np.sum((y_pred == 1) & (y_true == 0))
                fn = np.sum((y_pred == 0) & (y_true == 1))
                print(f"\n   ⚠️  Errores:")
                print(f"      • Falsos positivos: {fp}")
                print(f"      • Falsos negativos: {fn}")

        # Resumen global solo si hay múltiples condiciones
        if len(conditions_to_eval) > 1:
            self._print_multilabel_summary(metrics_by_condition, len(df))

    def _print_multilabel_summary(self, metrics_by_condition: Dict, total: int):
        """Imprime resumen global para evaluación multi-etiqueta."""
        print(f"\n{'-' * 40}")
        print("📊 RESUMEN GLOBAL MULTI-ETIQUETA")
        print(f"{'-' * 40}")

        # Calcular exact match (todas las condiciones correctas)
        all_correct = np.ones(total, dtype=bool)
        for cond, metrics in metrics_by_condition.items():
            all_correct &= (metrics['y_pred'] == metrics['y_true'])
        exact_match = np.mean(all_correct)
        print(f"   • Exact Match (todas correctas): {exact_match:.4f} ({exact_match:.2%})")

        # Hamming loss
        total_errors = sum(
            np.sum(m['y_pred'] != m['y_true']) for m in metrics_by_condition.values()
        )
        hamming = total_errors / (total * len(metrics_by_condition))
        print(f"   • Hamming Loss: {hamming:.4f}")

        # F1 promedio
        avg_f1 = np.mean([m['f1'] for m in metrics_by_condition.values()])
        print(f"   • F1-Score promedio: {avg_f1:.4f} ({avg_f1:.2%})")

        # Distribución de predicciones (para 2 condiciones)
        if len(metrics_by_condition) == 2:
            conds = list(metrics_by_condition.keys())
            y_pred_0 = metrics_by_condition[conds[0]]['y_pred']
            y_pred_1 = metrics_by_condition[conds[1]]['y_pred']

            both = np.sum((y_pred_0 == 1) & (y_pred_1 == 1))
            only_first = np.sum((y_pred_0 == 1) & (y_pred_1 == 0))
            only_second = np.sum((y_pred_0 == 0) & (y_pred_1 == 1))
            neither = np.sum((y_pred_0 == 0) & (y_pred_1 == 0))

            print(f"\n   📈 Distribución de predicciones:")
            print(f"      • Ambos trastornos:    {both} ({both/total:.1%})")
            print(f"      • Solo {conds[0]}:      {only_first} ({only_first/total:.1%})")
            print(f"      • Solo {conds[1]}:       {only_second} ({only_second/total:.1%})")
            print(f"      • Ninguno:             {neither} ({neither/total:.1%})")

    def _print_summary(self, results: List[Dict]):
        """Imprime resumen de resultados."""
        if not results:
            return

        print("\n" + "=" * 80)
        print("📊 RESUMEN DE RESULTADOS")
        print("=" * 80)

        total = len(results)

        # Verificar si es multi-etiqueta
        is_multilabel = 'has_anxiety' in results[0]

        if is_multilabel:
            with_depression = sum(1 for r in results if r['prediction'] == 1)
            with_anxiety = sum(1 for r in results if r.get('has_anxiety', False))
            both = sum(1 for r in results if r['prediction'] == 1 and r.get('has_anxiety', False))
            neither = sum(1 for r in results if r['prediction'] == 0 and not r.get('has_anxiety', False))

            matches_dep = sum(1 for r in results if r.get('match_dep', False))
            matches_anx = sum(1 for r in results if r.get('match_anx', False))
            matches_both = sum(1 for r in results if r['match'])

            avg_prob_dep = np.mean([r['probability'] for r in results])
            avg_prob_anx = np.mean([r.get('anxiety_probability', 0) for r in results])

            print(f"\n📈 Estadísticas Multi-Etiqueta:")
            print(f"   • Total analizado: {total}")

            print(f"\n   📌 DEPRESIÓN:")
            print(f"      • Detectada:           {with_depression} ({with_depression/total:.1%})")
            print(f"      • Coincide heurística: {matches_dep} ({matches_dep/total:.1%})")
            print(f"      • Prob. promedio:      {avg_prob_dep:.2%}")

            print(f"\n   📌 ANSIEDAD:")
            print(f"      • Detectada:           {with_anxiety} ({with_anxiety/total:.1%})")
            print(f"      • Coincide heurística: {matches_anx} ({matches_anx/total:.1%})")
            print(f"      • Prob. promedio:      {avg_prob_anx:.2%}")

            print(f"\n   📌 COMBINACIONES:")
            print(f"      • Ambos trastornos:    {both} ({both/total:.1%})")
            print(f"      • Ninguno:             {neither} ({neither/total:.1%})")
            print(f"      • Coincide TODO:       {matches_both} ({matches_both/total:.1%})")
        else:
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
            if self.pipeline.is_multi_label:
                heuristic_labels = self.preprocessor.detect_multi_label(clean_text_str)
                heuristic_dep = heuristic_labels[0]
                heuristic_anx = heuristic_labels[1]

                print(f"\n🔍 Comparación con Heurística:")
                print(f"   📌 DEPRESIÓN:")
                print(f"      • Modelo predice:     {'Sí ⚠️' if details['has_depression'] else 'No ✅'}")
                print(f"      • Heurística detecta: {'Sí' if heuristic_dep == 1 else 'No'}")
                print(f"      • Coinciden:          {'✅ Sí' if details['has_depression'] == (heuristic_dep == 1) else '❌ No'}")

                print(f"   📌 ANSIEDAD:")
                print(f"      • Modelo predice:     {'Sí ⚠️' if details.get('has_anxiety', False) else 'No ✅'}")
                print(f"      • Heurística detecta: {'Sí' if heuristic_anx == 1 else 'No'}")
                print(f"      • Coinciden:          {'✅ Sí' if details.get('has_anxiety', False) == (heuristic_anx == 1) else '❌ No'}")

                dep_match = details['has_depression'] == (heuristic_dep == 1)
                anx_match = details.get('has_anxiety', False) == (heuristic_anx == 1)

                results.append({
                    'index': idx,
                    'prediction': prediction,
                    'probability': prob,
                    'has_anxiety': details.get('has_anxiety', False),
                    'anxiety_probability': details.get('probability_anxiety', 0),
                    'heuristic_dep': heuristic_dep,
                    'heuristic_anx': heuristic_anx,
                    'match_dep': dep_match,
                    'match_anx': anx_match,
                    'match': dep_match and anx_match
                })
            else:
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
        '--condition',
        type=str,
        nargs='+',
        default=['all'],
        choices=['all', 'depression', 'anxiety'],
        help='Condiciones a evaluar: all (multi-label), depression, anxiety. Ejemplos: --condition all, --condition depression, --condition anxiety'
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
            tester.test_full_dataset(conditions=args.condition)

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
