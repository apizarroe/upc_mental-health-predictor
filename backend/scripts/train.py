#!/usr/bin/env python3
"""
Script CLI para entrenar el modelo BERT + XGBoost
para detección de depresión.

Uso:
    python scripts/train.py
    python scripts/train.py --bert-model dccuchile/bert-base-spanish-wwm-cased
    python scripts/train.py --data-path data/datasets/custom_data.parquet
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

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.ml.training_pipeline import TrainingPipeline


def parse_args():
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Entrenar modelo BERT + XGBoost para detección de depresión',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
    # Entrenamiento básico
    python scripts/train.py

    # Con modelo BERT específico
    python scripts/train.py --bert-model bert-base-multilingual-cased

    # Con datos personalizados
    python scripts/train.py --data-path mi_dataset.parquet

    # Configuración personalizada
    python scripts/train.py --test-size 0.25 --batch-size 32 --n-estimators 200
        """
    )

    parser.add_argument(
        '--data-path',
        type=str,
        default='data/datasets/train-00000-of-00001.parquet',
        help='Ruta al archivo parquet con datos de entrenamiento'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/trained_models',
        help='Directorio donde guardar el modelo entrenado'
    )

    parser.add_argument(
        '--bert-model',
        type=str,
        default='dccuchile/bert-base-spanish-wwm-cased',
        help='Nombre del modelo BERT pre-entrenado a usar'
    )

    parser.add_argument(
        '--model-name',
        type=str,
        default=None,
        help='Nombre para el modelo guardado (default: timestamp)'
    )

    parser.add_argument(
        '--test-size',
        type=float,
        default=0.2,
        help='Proporción de datos para test (default: 0.2)'
    )

    parser.add_argument(
        '--val-size',
        type=float,
        default=0.1,
        help='Proporción de datos para validación (default: 0.1)'
    )

    parser.add_argument(
        '--max-length',
        type=int,
        default=512,
        help='Longitud máxima de tokens para BERT (default: 512)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=16,
        help='Tamaño de batch para BERT (default: 16)'
    )

    parser.add_argument(
        '--n-estimators',
        type=int,
        default=100,
        help='Número de estimadores para XGBoost (default: 100)'
    )

    parser.add_argument(
        '--max-depth',
        type=int,
        default=6,
        help='Profundidad máxima de árboles XGBoost (default: 6)'
    )

    parser.add_argument(
        '--learning-rate',
        type=float,
        default=0.1,
        help='Tasa de aprendizaje XGBoost (default: 0.1)'
    )

    parser.add_argument(
        '--random-state',
        type=int,
        default=42,
        help='Semilla aleatoria para reproducibilidad (default: 42)'
    )

    return parser.parse_args()


def main():
    """Función principal."""
    args = parse_args()

    # Verificar que existe el archivo de datos
    data_path = Path(args.data_path)
    if not data_path.exists():
        print(f"❌ Error: No se encontró el archivo de datos: {data_path}")
        print(f"   Ruta completa: {data_path.absolute()}")
        sys.exit(1)

    print("🚀 Iniciando entrenamiento de modelo")
    print(f"   • Datos: {data_path}")
    print(f"   • Modelo BERT: {args.bert_model}")
    print(f"   • Output: {args.output_dir}")
    print()

    try:
        # Crear pipeline
        pipeline = TrainingPipeline(
            data_path=str(data_path),
            output_dir=args.output_dir,
            test_size=args.test_size,
            val_size=args.val_size,
            random_state=args.random_state
        )

        # Preparar datos
        pipeline.prepare_data()

        # Generar embeddings
        pipeline.generate_embeddings(
            model_name=args.bert_model,
            max_length=args.max_length,
            batch_size=args.batch_size
        )

        # Dividir datos
        pipeline.split_data()

        # Entrenar clasificador
        pipeline.train_classifier(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            learning_rate=args.learning_rate
        )

        # Evaluar
        test_metrics = pipeline.evaluate()

        # Guardar modelo
        model_path, metadata_path = pipeline.save_model(args.model_name)

        print("\n" + "=" * 80)
        print("✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        print(f"\n📊 Resultados finales (Test Set):")
        print(f"   • Accuracy:  {test_metrics['accuracy']:.4f}")
        print(f"   • Precision: {test_metrics['precision']:.4f}")
        print(f"   • Recall:    {test_metrics['recall']:.4f}")
        print(f"   • F1-Score:  {test_metrics['f1_score']:.4f}")
        print(f"\n💾 Archivos guardados:")
        print(f"   • {model_path}")
        print(f"   • {metadata_path}")
        print(f"\n🎯 Próximo paso: Validar el modelo")
        print(f"   python scripts/test.py --random 10")
        print()

        # Salida limpia
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Entrenamiento interrumpido por el usuario")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error durante el entrenamiento: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
