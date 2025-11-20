#!/usr/bin/env python3
"""
Script para leer y visualizar archivos parquet en formato tabla.
Uso: python read_parquet.py [--rows N] [--columns col1,col2,...]
"""

import pandas as pd
import argparse
from pathlib import Path
import sys


def read_parquet_file(file_path, num_rows=None, columns=None):
    """
    Lee un archivo parquet y lo muestra en formato tabla.

    Args:
        file_path: Ruta al archivo parquet
        num_rows: Número de filas a mostrar (None = todas)
        columns: Lista de columnas específicas a mostrar (None = todas)
    """
    try:
        # Leer el archivo parquet
        print(f"📂 Leyendo archivo: {file_path}")
        print("-" * 80)

        df = pd.read_parquet(file_path)

        # Información básica del dataset
        print(f"\n📊 INFORMACIÓN DEL DATASET")
        print(f"   • Filas: {len(df):,}")
        print(f"   • Columnas: {len(df.columns)}")
        print(f"   • Tamaño en memoria: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        # Mostrar columnas disponibles
        print(f"\n📋 COLUMNAS DISPONIBLES:")
        for i, col in enumerate(df.columns, 1):
            dtype = df[col].dtype
            null_count = df[col].isna().sum()
            null_pct = (null_count / len(df)) * 100
            print(f"   {i:2d}. {col:30s} | Tipo: {str(dtype):15s} | Nulos: {null_count:5d} ({null_pct:.1f}%)")

        # Filtrar columnas si se especificaron
        if columns:
            available_cols = df.columns.tolist()
            invalid_cols = [col for col in columns if col not in available_cols]
            if invalid_cols:
                print(f"\n⚠️  Columnas no encontradas: {', '.join(invalid_cols)}")
                return
            df = df[columns]
            print(f"\n🔍 Mostrando solo columnas: {', '.join(columns)}")

        # Estadísticas descriptivas
        print(f"\n📈 ESTADÍSTICAS DESCRIPTIVAS:")
        print(df.describe(include='all').to_string())

        # Mostrar primeras filas
        print(f"\n📄 PRIMERAS {num_rows if num_rows else 'TODAS LAS'} FILAS:")
        print("-" * 80)

        # Configurar pandas para mejor visualización
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 100)

        # Verificar si hay columnas con datos tipo lista/dict (conversaciones)
        if 'chat' in df.columns and isinstance(df['chat'].iloc[0], list):
            print("\n🗣️  CONVERSACIONES (formato expandido):")
            print("-" * 80)
            rows_to_show = num_rows if num_rows else len(df)
            for idx in range(min(rows_to_show, len(df))):
                print(f"\n📝 CONVERSACIÓN #{idx + 1}:")
                print("=" * 80)
                conversation = df['chat'].iloc[idx]
                for i, message in enumerate(conversation, 1):
                    role = message.get('role', 'unknown')
                    content = message.get('content', '')

                    # Emoji según el rol
                    emoji = {
                        'system': '⚙️ ',
                        'user': '👤',
                        'assistant': '🤖'
                    }.get(role, '❓')

                    print(f"\n   {emoji} {role.upper()}:")
                    # Mostrar contenido con indentación
                    for line in content.split('\n'):
                        print(f"      {line}")

                if idx < rows_to_show - 1:
                    print("\n" + "-" * 80)
        else:
            if num_rows:
                print(df.head(num_rows).to_string(index=True))
            else:
                print(df.to_string(index=True))

        # Información sobre valores únicos en columnas categóricas
        print(f"\n🏷️  VALORES ÚNICOS EN COLUMNAS CATEGÓRICAS:")
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            # Verificar si la columna contiene listas/dicts (datos anidados)
            if isinstance(df[col].iloc[0], (list, dict)):
                print(f"\n   {col}: Contiene datos anidados (conversaciones/objetos complejos)")
                continue

            try:
                unique_count = df[col].nunique()
                if unique_count <= 20:  # Solo mostrar si hay menos de 20 valores únicos
                    values = df[col].value_counts().head(10)
                    print(f"\n   {col}:")
                    for val, count in values.items():
                        pct = (count / len(df)) * 100
                        print(f"      • {val}: {count} ({pct:.1f}%)")
                    if unique_count > 10:
                        print(f"      ... y {unique_count - 10} valores más")
                else:
                    print(f"\n   {col}: {unique_count} valores únicos (demasiados para mostrar)")
            except Exception as e:
                print(f"\n   {col}: No se puede procesar (tipo de dato complejo)")

        # Verificar valores nulos
        null_cols = df.columns[df.isna().any()].tolist()
        if null_cols:
            print(f"\n⚠️  COLUMNAS CON VALORES NULOS:")
            for col in null_cols:
                null_count = df[col].isna().sum()
                null_pct = (null_count / len(df)) * 100
                print(f"   • {col}: {null_count} nulos ({null_pct:.1f}%)")

        print(f"\n✅ Lectura completada exitosamente!")

    except FileNotFoundError:
        print(f"❌ Error: Archivo no encontrado: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al leer el archivo: {str(e)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Lee y visualiza archivos parquet en formato tabla',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python read_parquet.py
  python read_parquet.py --rows 10
  python read_parquet.py --columns text,label
  python read_parquet.py --rows 20 --columns text,label,sentiment
        """
    )

    parser.add_argument(
        '--file',
        type=str,
        default='train-00000-of-00001.parquet',
        help='Ruta al archivo parquet (default: backend/data/datasets/train-00000-of-00001.parquet)'
    )

    parser.add_argument(
        '--rows',
        type=int,
        default=10,
        help='Número de filas a mostrar (default: 10, usar 0 para todas)'
    )

    parser.add_argument(
        '--columns',
        type=str,
        help='Columnas específicas a mostrar, separadas por comas (ej: text,label)'
    )

    parser.add_argument(
        '--export-csv',
        type=str,
        help='Exportar a CSV con la ruta especificada'
    )

    args = parser.parse_args()

    # Convertir ruta relativa a absoluta
    file_path = Path(args.file)
    if not file_path.is_absolute():
        file_path = Path(__file__).parent / file_path

    # Procesar columnas
    columns = None
    if args.columns:
        columns = [col.strip() for col in args.columns.split(',')]

    # Número de filas (0 = todas)
    num_rows = None if args.rows == 0 else args.rows

    # Leer y mostrar el archivo
    read_parquet_file(file_path, num_rows, columns)

    # Exportar a CSV si se especificó
    if args.export_csv:
        try:
            df = pd.read_parquet(file_path)
            if columns:
                df = df[columns]
            df.to_csv(args.export_csv, index=False)
            print(f"\n💾 Datos exportados a: {args.export_csv}")
        except Exception as e:
            print(f"\n❌ Error al exportar CSV: {str(e)}")


if __name__ == "__main__":
    main()
