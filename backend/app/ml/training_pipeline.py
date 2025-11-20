"""
Pipeline completo de entrenamiento: BERT + XGBoost
para detección de depresión.
"""

import numpy as np
from sklearn.model_selection import train_test_split
from pathlib import Path
import json
from datetime import datetime

from .preprocessor import TextPreprocessor
from .bert_encoder import BERTEncoder
from .classifier import DepressionClassifier


class TrainingPipeline:
    """Pipeline completo de entrenamiento del modelo."""

    def __init__(
        self,
        data_path: str,
        output_dir: str = "../../data/trained_models",
        test_size: float = 0.2,
        val_size: float = 0.1,
        random_state: int = 42
    ):
        """
        Inicializa el pipeline de entrenamiento.

        Args:
            data_path: Ruta al archivo parquet con datos
            output_dir: Directorio para guardar modelos
            test_size: Proporción de datos para test
            val_size: Proporción de datos para validación
            random_state: Semilla aleatoria
        """
        self.data_path = data_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state

        # Componentes del pipeline
        self.preprocessor = None
        self.encoder = None
        self.classifier = None

        # Datos
        self.texts = None
        self.labels = None
        self.embeddings = None

        print("=" * 80)
        print("🎯 ENTRENAMIENTO DE MODELO BERT + XGBOOST")
        print("   Detección de Depresión")
        print("=" * 80)

    def prepare_data(self):
        """Prepara los datos: carga y preprocesa."""
        print("\n📦 PASO 1: Preparación de datos")
        print("-" * 80)

        self.preprocessor = TextPreprocessor()
        self.texts, self.labels = self.preprocessor.create_dataset(self.data_path)

        print(f"\n   Distribución de clases:")
        print(f"   • Depresión (1): {sum(self.labels)} ({sum(self.labels)/len(self.labels)*100:.1f}%)")
        print(f"   • No depresión (0): {len(self.labels) - sum(self.labels)} ({(1-sum(self.labels)/len(self.labels))*100:.1f}%)")

    def generate_embeddings(
        self,
        model_name: str = "dccuchile/bert-base-spanish-wwm-cased",
        max_length: int = 512,
        batch_size: int = 16
    ):
        """
        Genera embeddings BERT para todos los textos.

        Args:
            model_name: Modelo BERT a usar
            max_length: Longitud máxima de tokens
            batch_size: Tamaño de batch
        """
        print("\n🧠 PASO 2: Generación de embeddings BERT")
        print("-" * 80)

        self.encoder = BERTEncoder(
            model_name=model_name,
            max_length=max_length,
            batch_size=batch_size
        )

        self.embeddings = self.encoder.encode_texts(self.texts)

        print(f"\n   Embeddings generados: {self.embeddings.shape}")

    def split_data(self):
        """Divide los datos en train, validation y test."""
        print("\n✂️  PASO 3: División de datos")
        print("-" * 80)

        # Primero separar test
        X_temp, X_test, y_temp, y_test = train_test_split(
            self.embeddings,
            self.labels,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=self.labels
        )

        # Luego separar train y validation
        val_size_adjusted = self.val_size / (1 - self.test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp,
            y_temp,
            test_size=val_size_adjusted,
            random_state=self.random_state,
            stratify=y_temp
        )

        self.data_splits = {
            'X_train': X_train,
            'X_val': X_val,
            'X_test': X_test,
            'y_train': np.array(y_train),
            'y_val': np.array(y_val),
            'y_test': np.array(y_test)
        }

        print(f"   • Training set:   {len(y_train)} samples")
        print(f"   • Validation set: {len(y_val)} samples")
        print(f"   • Test set:       {len(y_test)} samples")

    def train_classifier(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1
    ):
        """
        Entrena el clasificador XGBoost.

        Args:
            n_estimators: Número de árboles
            max_depth: Profundidad máxima
            learning_rate: Tasa de aprendizaje
        """
        print("\n🚀 PASO 4: Entrenamiento del clasificador XGBoost")
        print("-" * 80)

        self.classifier = DepressionClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=self.random_state
        )

        self.metrics = self.classifier.train(
            self.data_splits['X_train'],
            self.data_splits['y_train'],
            self.data_splits['X_val'],
            self.data_splits['y_val']
        )

    def evaluate(self):
        """Evalúa el modelo en el conjunto de test."""
        print("\n📊 PASO 5: Evaluación en conjunto de prueba")
        print("-" * 80)

        test_metrics = self.classifier.evaluate(
            self.data_splits['X_test'],
            self.data_splits['y_test']
        )

        self.metrics['test'] = test_metrics

        return test_metrics

    def save_model(self, model_name: str = None):
        """
        Guarda el modelo y metadatos.

        Args:
            model_name: Nombre del modelo (usa timestamp si es None)
        """
        print("\n💾 PASO 6: Guardando modelo")
        print("-" * 80)

        if model_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"depression_bert_xgboost_{timestamp}"

        # Guardar clasificador
        model_path = self.output_dir / f"{model_name}.pkl"
        self.classifier.save(str(model_path))

        # Guardar metadatos
        metadata = {
            'model_name': model_name,
            'created_at': datetime.now().isoformat(),
            'bert_model': self.encoder.model_name,
            'embedding_dim': self.encoder.get_embedding_dim(),
            'n_samples': len(self.labels),
            'n_train': len(self.data_splits['y_train']),
            'n_val': len(self.data_splits['y_val']),
            'n_test': len(self.data_splits['y_test']),
            'metrics': {
                'train': self.metrics['train'],
                'val': self.metrics['val'],
                'test': self.metrics['test']
            },
            'xgboost_params': self.classifier.params
        }

        metadata_path = self.output_dir / f"{model_name}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)

        print(f"   • Modelo: {model_path}")
        print(f"   • Metadata: {metadata_path}")

        return model_path, metadata_path

    def run_complete_pipeline(
        self,
        bert_model: str = "dccuchile/bert-base-spanish-wwm-cased",
        model_name: str = None
    ):
        """
        Ejecuta el pipeline completo de entrenamiento.

        Args:
            bert_model: Modelo BERT a usar
            model_name: Nombre para guardar el modelo

        Returns:
            Métricas finales
        """
        # 1. Preparar datos
        self.prepare_data()

        # 2. Generar embeddings
        self.generate_embeddings(model_name=bert_model)

        # 3. Dividir datos
        self.split_data()

        # 4. Entrenar
        self.train_classifier()

        # 5. Evaluar
        test_metrics = self.evaluate()

        # 6. Guardar
        self.save_model(model_name)

        print("\n" + "=" * 80)
        print("✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE!")
        print("=" * 80)

        return test_metrics


if __name__ == "__main__":
    # Ejemplo de uso
    data_path = "../../data/datasets/train-00000-of-00001.parquet"

    pipeline = TrainingPipeline(
        data_path=data_path,
        test_size=0.2,
        val_size=0.1
    )

    # Ejecutar pipeline completo
    metrics = pipeline.run_complete_pipeline()

    print("\n🎉 Modelo entrenado y guardado!")
