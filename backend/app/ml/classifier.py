"""
Clasificador XGBoost para detección de depresión.
Usa embeddings BERT como features.
"""

import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
import pickle
from typing import Tuple, Dict
from pathlib import Path


class DepressionClassifier:
    """Clasificador XGBoost para detectar depresión en textos."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        random_state: int = 42
    ):
        """
        Inicializa el clasificador XGBoost.

        Args:
            n_estimators: Número de árboles
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

        self.model = xgb.XGBClassifier(**self.params)
        self.is_trained = False

        print("🔧 Inicializado clasificador XGBoost")
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
        Entrena el clasificador.

        Args:
            X_train: Features de entrenamiento (embeddings BERT)
            y_train: Etiquetas de entrenamiento
            X_val: Features de validación (opcional)
            y_val: Etiquetas de validación (opcional)
            verbose: Mostrar progreso

        Returns:
            Diccionario con métricas de entrenamiento
        """
        print("\n🚀 Iniciando entrenamiento...")

        eval_set = [(X_train, y_train)]
        if X_val is not None and y_val is not None:
            eval_set.append((X_val, y_val))

        self.model.fit(
            X_train,
            y_train,
            eval_set=eval_set,
            verbose=verbose
        )

        self.is_trained = True

        # Calcular métricas en training
        train_preds = self.model.predict(X_train)
        train_metrics = self._calculate_metrics(y_train, train_preds, "Training")

        # Calcular métricas en validación si existe
        val_metrics = {}
        if X_val is not None and y_val is not None:
            val_preds = self.model.predict(X_val)
            val_metrics = self._calculate_metrics(y_val, val_preds, "Validation")

        print("\n✅ Entrenamiento completado!")

        return {
            'train': train_metrics,
            'val': val_metrics
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predice etiquetas para nuevos datos.

        Args:
            X: Features (embeddings BERT)

        Returns:
            Array de predicciones (0 o 1)
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado primero")

        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predice probabilidades para nuevos datos.

        Args:
            X: Features (embeddings BERT)

        Returns:
            Array de probabilidades [prob_no_depresion, prob_depresion]
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado primero")

        return self.model.predict_proba(X)

    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict:
        """
        Evalúa el modelo en datos de prueba.

        Args:
            X_test: Features de prueba
            y_test: Etiquetas verdaderas

        Returns:
            Diccionario con métricas
        """
        predictions = self.predict(X_test)
        return self._calculate_metrics(y_test, predictions, "Test")

    def _calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        dataset_name: str
    ) -> Dict:
        """
        Calcula métricas de evaluación.

        Args:
            y_true: Etiquetas verdaderas
            y_pred: Predicciones
            dataset_name: Nombre del dataset para logging

        Returns:
            Diccionario con métricas
        """
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        cm = confusion_matrix(y_true, y_pred)

        print(f"\n📊 Métricas en {dataset_name}:")
        print(f"   • Accuracy:  {accuracy:.4f}")
        print(f"   • Precision: {precision:.4f}")
        print(f"   • Recall:    {recall:.4f}")
        print(f"   • F1-Score:  {f1:.4f}")
        print(f"\n   Matriz de Confusión:")
        print(f"   {cm}")

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm.tolist()
        }

    def save(self, filepath: str):
        """
        Guarda el modelo entrenado.

        Args:
            filepath: Ruta donde guardar el modelo
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado primero")

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)

        print(f"💾 Modelo guardado en: {filepath}")

    def load(self, filepath: str):
        """
        Carga un modelo entrenado.

        Args:
            filepath: Ruta del modelo guardado
        """
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)

        self.is_trained = True
        print(f"📂 Modelo cargado desde: {filepath}")

    def get_feature_importance(self, top_n: int = 20) -> np.ndarray:
        """
        Retorna la importancia de las features.

        Args:
            top_n: Número de features más importantes a retornar

        Returns:
            Array con importancias ordenadas
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado primero")

        importances = self.model.feature_importances_
        top_indices = np.argsort(importances)[-top_n:][::-1]

        print(f"\n🔝 Top {top_n} Features más importantes:")
        for i, idx in enumerate(top_indices, 1):
            print(f"   {i}. Feature {idx}: {importances[idx]:.4f}")

        return importances[top_indices]


if __name__ == "__main__":
    # Ejemplo de uso
    from sklearn.datasets import make_classification

    # Generar datos de ejemplo
    X, y = make_classification(
        n_samples=1000,
        n_features=768,  # Dimensión típica de BERT
        n_informative=100,
        n_redundant=50,
        random_state=42
    )

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Entrenar clasificador
    classifier = DepressionClassifier()
    metrics = classifier.train(X_train, y_train, X_test, y_test)

    # Evaluar
    test_metrics = classifier.evaluate(X_test, y_test)
