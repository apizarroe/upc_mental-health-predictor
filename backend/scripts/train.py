#!/usr/bin/env python3
"""
Script CLI para entrenar el modelo BERT + XGBoost
para detección de trastornos mentales.

Soporta modelos binarios (solo depresión) y multi-etiqueta (depresión + ansiedad).

Uso:
    # Entrenar modelo multi-etiqueta (default)
    python scripts/train.py

    # Entrenar modelo binario (solo depresión)
    python scripts/train.py --binary

    # Con modelo BERT específico
    python scripts/train.py --bert-model dccuchile/bert-base-spanish-wwm-cased

    # Con datos personalizados
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
        description='Entrenar modelo BERT + XGBoost para detección de trastornos mentales',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
    # Entrenamiento multi-etiqueta (depresión + ansiedad) - DEFAULT
    python scripts/train.py

    # Entrenamiento binario (solo depresión)
    python scripts/train.py --binary

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
        default='PlanTL-GOB-ES/roberta-base-biomedical-es',
        help='Nombre del modelo BERT/RoBERTa pre-entrenado a usar'
    )

    parser.add_argument(
        '--model-name',
        type=str,
        default=None,
        help='Nombre para el modelo guardado (default: timestamp)'
    )

    parser.add_argument(
        '--binary',
        action='store_true',
        help='Entrenar modelo binario (solo depresión). Por defecto entrena multi-etiqueta.'
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
        default=150,
        help='Número de estimadores para XGBoost (default: 150)'
    )

    parser.add_argument(
        '--max-depth',
        type=int,
        default=5,
        help='Profundidad máxima de árboles XGBoost (default: 5)'
    )

    parser.add_argument(
        '--learning-rate',
        type=float,
        default=0.08,
        help='Tasa de aprendizaje XGBoost (default: 0.08)'
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

    # Determinar tipo de modelo
    multi_label = not args.binary
    model_type_str = "Multi-Etiqueta (Depresión + Ansiedad)" if multi_label else "Binario (Solo Depresión)"

    # Verificar que existe el archivo de datos
    data_path = Path(args.data_path)
    if not data_path.exists():
        print(f"❌ Error: No se encontró el archivo de datos: {data_path}")
        print(f"   Ruta completa: {data_path.absolute()}")
        sys.exit(1)

    print("🚀 Iniciando entrenamiento de modelo")
    print(f"   • Tipo: {model_type_str}")
    print(f"   • Datos: {data_path}")
    print(f"   • Modelo BERT: {args.bert_model}")
    print(f"   • Output: {args.output_dir}")
    print()

    try:
        # Crear pipeline con soporte multi-etiqueta
        pipeline = TrainingPipeline(
            data_path=str(data_path),
            output_dir=args.output_dir,
            test_size=args.test_size,
            val_size=args.val_size,
            random_state=args.random_state,
            multi_label=multi_label
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

        # Mostrar métricas según tipo de modelo
        print(f"\n📊 Resultados finales (Test Set):")

        if multi_label:
            # Métricas multi-etiqueta
            for label in ['depression', 'anxiety']:
                if label in test_metrics:
                    m = test_metrics[label]
                    print(f"\n   📌 {label.upper()}:")
                    print(f"      • Accuracy:  {m.get('accuracy', 0):.4f}")
                    print(f"      • Precision: {m.get('precision', 0):.4f}")
                    print(f"      • Recall:    {m.get('recall', 0):.4f}")
                    print(f"      • F1-Score:  {m.get('f1_score', 0):.4f}")

            if 'overall' in test_metrics:
                print(f"\n   📈 OVERALL:")
                print(f"      • Avg Accuracy:  {test_metrics['overall'].get('avg_accuracy', 0):.4f}")
                print(f"      • Avg F1-Score:  {test_metrics['overall'].get('avg_f1_score', 0):.4f}")
        else:
            # Métricas binarias
            print(f"   • Accuracy:  {test_metrics.get('accuracy', 0):.4f}")
            print(f"   • Precision: {test_metrics.get('precision', 0):.4f}")
            print(f"   • Recall:    {test_metrics.get('recall', 0):.4f}")
            print(f"   • F1-Score:  {test_metrics.get('f1_score', 0):.4f}")

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
