"""
Clasificador Multi-Etiqueta XGBoost para detección de trastornos mentales.
Predice simultáneamente depresión y ansiedad usando embeddings BERT.
"""

import numpy as np
import xgboost as xgb
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
import pickle
from typing import Dict, List, Tuple
from pathlib import Path


class MultiLabelMentalHealthClassifier:
    """
    Clasificador Multi-Etiqueta XGBoost para detectar múltiples trastornos.

    Predice simultáneamente:
    - Depresión (0/1)
    - Ansiedad (0/1)

    Usa MultiOutputClassifier de sklearn que entrena un clasificador
    independiente para cada etiqueta, pero comparte los mismos embeddings.
    """

    # Nombres de las etiquetas en orden
    LABEL_NAMES = ['depression', 'anxiety']

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        random_state: int = 42
    ):
        """
        Inicializa el clasificador multi-etiqueta.

        Args:
            n_estimators: Número de árboles por clasificador
            max_depth: Profundidad máxima de cada árbol
            learning_rate: Tasa de aprendizaje
            random_state: Semilla aleatoria para reproducibilidad
        """
        self.params = {
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'learning_rate': learning_rate,
            'random_state': random_state,
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'use_label_encoder': False
        }

        # Crear clasificador base XGBoost
        base_classifier = xgb.XGBClassifier(**self.params)

        # Envolver en MultiOutputClassifier para multi-etiqueta
        self.model = MultiOutputClassifier(base_classifier)
        self.is_trained = False

        print("🔧 Inicializado clasificador Multi-Etiqueta XGBoost")
        print(f"   • Etiquetas: {self.LABEL_NAMES}")
        print(f"   • Estimadores: {n_estimators}")
        print(f"   • Max depth: {max_depth}")
        print(f"   • Learning rate: {learning_rate}")

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None,
        verbose: bool = True
    ) -> Dict:
        """
        Entrena el clasificador multi-etiqueta.

        Args:
            X_train: Features de entrenamiento (embeddings BERT) shape (N, 768)
            y_train: Etiquetas de entrenamiento shape (N, 2) - [depression, anxiety]
            X_val: Features de validación (opcional)
            y_val: Etiquetas de validación (opcional)
            verbose: Mostrar progreso

        Returns:
            Diccionario con métricas de entrenamiento por etiqueta
        """
        print("\n🚀 Iniciando entrenamiento multi-etiqueta...")
        print(f"   • Samples de entrenamiento: {X_train.shape[0]}")
        print(f"   • Dimensión embeddings: {X_train.shape[1]}")
        print(f"   • Etiquetas: {y_train.shape[1]}")

        # Entrenar modelo
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Calcular métricas en training
        train_preds = self.model.predict(X_train)
        train_metrics = self._calculate_metrics_per_label(
            y_train, train_preds, "Training"
        )

        # Calcular métricas en validación si existe
        val_metrics = {}
        if X_val is not None and y_val is not None:
            val_preds = self.model.predict(X_val)
            val_metrics = self._calculate_metrics_per_label(
                y_val, val_preds, "Validation"
            )

        print("\n✅ Entrenamiento multi-etiqueta completado!")

        return {
            'train': train_metrics,
            'val': val_metrics
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predice etiquetas para nuevos datos.

        Args:
            X: Features (embeddings BERT) shape (N, 768)

        Returns:
            Array de predicciones shape (N, 2) - [[dep, anx], ...]
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado primero")

        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> List[np.ndarray]:
        """
        Predice probabilidades para nuevos datos.

        Args:
            X: Features (embeddings BERT) shape (N, 768)

        Returns:
            Lista de 2 arrays:
            - [0]: Probabilidades depresión shape (N, 2) - [P(no), P(si)]
            - [1]: Probabilidades ansiedad shape (N, 2) - [P(no), P(si)]
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado primero")

        return self.model.predict_proba(X)

    def predict_with_proba(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Predice etiquetas y probabilidades en formato estructurado.

        Args:
            X: Features (embeddings BERT) shape (N, 768)

        Returns:
            Diccionario con predicciones y probabilidades:
            {
                'predictions': ndarray (N, 2),
                'probabilities': {
                    'depression': ndarray (N,) - P(depression=1),
                    'anxiety': ndarray (N,) - P(anxiety=1)
                }
            }
        """
        predictions = self.predict(X)
        probas = self.predict_proba(X)

        return {
            'predictions': predictions,
            'probabilities': {
                'depression': probas[0][:, 1],  # P(depression=1)
                'anxiety': probas[1][:, 1]       # P(anxiety=1)
            }
        }

    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict:
        """
        Evalúa el modelo en datos de prueba.

        Args:
            X_test: Features de prueba
            y_test: Etiquetas verdaderas shape (N, 2)

        Returns:
            Diccionario con métricas por etiqueta
        """
        predictions = self.predict(X_test)
        return self._calculate_metrics_per_label(y_test, predictions, "Test")

    def _calculate_metrics_per_label(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        dataset_name: str
    ) -> Dict:
        """
        Calcula métricas de evaluación por cada etiqueta.

        Args:
            y_true: Etiquetas verdaderas shape (N, 2)
            y_pred: Predicciones shape (N, 2)
            dataset_name: Nombre del dataset para logging

        Returns:
            Diccionario con métricas por etiqueta
        """
        metrics = {}

        print(f"\n📊 Métricas en {dataset_name}:")
        print("=" * 60)

        for i, label_name in enumerate(self.LABEL_NAMES):
            y_true_label = y_true[:, i]
            y_pred_label = y_pred[:, i]

            accuracy = accuracy_score(y_true_label, y_pred_label)
            precision = precision_score(y_true_label, y_pred_label, zero_division=0)
            recall = recall_score(y_true_label, y_pred_label, zero_division=0)
            f1 = f1_score(y_true_label, y_pred_label, zero_division=0)
            cm = confusion_matrix(y_true_label, y_pred_label)

            metrics[label_name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'confusion_matrix': cm.tolist()
            }

            print(f"\n   📌 {label_name.upper()}:")
            print(f"      • Accuracy:  {accuracy:.4f}")
            print(f"      • Precision: {precision:.4f}")
            print(f"      • Recall:    {recall:.4f}")
            print(f"      • F1-Score:  {f1:.4f}")
            print(f"      • Confusion Matrix: {cm.tolist()}")

        # Métricas globales (promedio)
        avg_accuracy = np.mean([m['accuracy'] for m in metrics.values()])
        avg_f1 = np.mean([m['f1_score'] for m in metrics.values()])

        metrics['overall'] = {
            'avg_accuracy': avg_accuracy,
            'avg_f1_score': avg_f1
        }

        print(f"\n   📈 OVERALL:")
        print(f"      • Avg Accuracy: {avg_accuracy:.4f}")
        print(f"      • Avg F1-Score: {avg_f1:.4f}")

        return metrics

    def save(self, filepath: str):
        """
        Guarda el modelo entrenado.

        Args:
            filepath: Ruta donde guardar el modelo
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado primero")

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # Guardar el modelo completo (MultiOutputClassifier)
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)

        print(f"💾 Modelo multi-etiqueta guardado en: {filepath}")

    def load(self, filepath: str):
        """
        Carga un modelo entrenado.

        Args:
            filepath: Ruta del modelo guardado
        """
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)

        self.is_trained = True
        print(f"📂 Modelo multi-etiqueta cargado desde: {filepath}")


# Mantener compatibilidad con código existente
DepressionClassifier = MultiLabelMentalHealthClassifier


if __name__ == "__main__":
    # Ejemplo de uso
    from sklearn.datasets import make_multilabel_classification
    from sklearn.model_selection import train_test_split

    print("=" * 60)
    print("🧪 EJEMPLO DE USO - MultiLabelMentalHealthClassifier")
    print("=" * 60)

    # Generar datos de ejemplo multi-etiqueta
    X, y = make_multilabel_classification(
        n_samples=1000,
        n_features=768,  # Dimensión típica de BERT
        n_classes=2,      # depression, anxiety
        n_labels=1,       # Promedio de etiquetas por sample
        random_state=42
    )

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Entrenar clasificador
    classifier = MultiLabelMentalHealthClassifier()
    metrics = classifier.train(X_train, y_train, X_test, y_test)

    # Evaluar
    test_metrics = classifier.evaluate(X_test, y_test)

    # Ejemplo de predicción
    print("\n" + "=" * 60)
    print("🔮 EJEMPLO DE PREDICCIÓN")
    print("=" * 60)

    sample = X_test[:3]
    result = classifier.predict_with_proba(sample)

    for i in range(3):
        print(f"\n   Sample {i+1}:")
        print(f"      Depression: {result['predictions'][i][0]} (prob: {result['probabilities']['depression'][i]:.2%})")
        print(f"      Anxiety:    {result['predictions'][i][1]} (prob: {result['probabilities']['anxiety'][i]:.2%})")
