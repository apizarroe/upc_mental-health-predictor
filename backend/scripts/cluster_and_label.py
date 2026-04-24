#!/usr/bin/env python3
"""
Auto-etiquetado del dataset usando keyword scores ponderados.

Estrategia por ejemplo individual (sin clustering):
  score_dep >= 2  y  score_dep > score_anx  → depression
  score_anx >= 2  y  score_anx > score_dep  → anxiety
  score_dep >= 2  y  score_anx >= 2          → depression (predominante si dep >= anx, sino anxiety)
  ambos < 2                                  → neutral

Guarda data/datasets/labeled_dataset.csv listo para entrenar.

Uso:
    python scripts/cluster_and_label.py
    python scripts/cluster_and_label.py --data-path data/datasets/train-00000-of-00001.parquet
    python scripts/cluster_and_label.py --threshold 2
"""

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import argparse
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.ml.text_processing import clean_text
from app.ml.keywords import DEPRESSION_KEYWORDS, ANXIETY_KEYWORDS

LABEL_MAP = {'depression': 0, 'anxiety': 1, 'neutral': 2}


def compute_score(text: str, keywords: dict) -> float:
    t = text.lower()
    return sum(w for kw, w in keywords.items() if kw in t)


def assign_label(dep: float, anx: float, threshold: float) -> str:
    dep_active = dep >= threshold
    anx_active = anx >= threshold

    if dep_active and anx_active:
        return 'depression' if dep >= anx else 'anxiety'
    if dep_active:
        return 'depression'
    if anx_active:
        return 'anxiety'
    return 'neutral'


def extract_user_messages(conversation) -> str:
    if not isinstance(conversation, list):
        return str(conversation)
    return ' '.join(
        msg.get('content', '')
        for msg in conversation
        if msg.get('role') == 'user'
    )


def main():
    parser = argparse.ArgumentParser(description='Auto-etiquetado por keyword scores')
    parser.add_argument('--data-path', default='data/datasets/train-00000-of-00001.parquet')
    parser.add_argument('--output', default='data/datasets/labeled_dataset.csv')
    parser.add_argument('--threshold', type=float, default=2.0,
                        help='Score mínimo para considerar una condición activa (default: 2)')
    args = parser.parse_args()

    data_path = backend_dir / args.data_path
    output_path = backend_dir / args.output

    print("=" * 70)
    print("AUTO-ETIQUETADO POR KEYWORD SCORES")
    print("=" * 70)

    # ------------------------------------------------------------------
    # PASO 1: Cargar y preprocesar
    # ------------------------------------------------------------------
    print(f"\n[1/3] Cargando dataset: {data_path}")
    df = pd.read_parquet(data_path)
    print(f"      {len(df)} conversaciones cargadas")

    texts_raw = [extract_user_messages(conv) for conv in df['chat']]
    texts_clean = [clean_text(t) for t in tqdm(texts_raw, desc='      Limpiando texto')]

    # ------------------------------------------------------------------
    # PASO 2: Calcular scores y asignar labels
    # ------------------------------------------------------------------
    print(f"\n[2/3] Calculando scores (threshold={args.threshold})")

    dep_scores = [compute_score(t, DEPRESSION_KEYWORDS) for t in texts_clean]
    anx_scores = [compute_score(t, ANXIETY_KEYWORDS) for t in texts_clean]
    labels = [assign_label(d, a, args.threshold) for d, a in zip(dep_scores, anx_scores)]
    label_ids = [LABEL_MAP[l] for l in labels]

    # Estadísticas
    from collections import Counter
    dist = Counter(labels)
    print(f"\n  Distribución de labels:")
    for label in ['depression', 'anxiety', 'neutral']:
        count = dist[label]
        pct = count / len(labels) * 100
        print(f"    {label:12s}: {count:5d} ({pct:.1f}%)")

    # Advertencia si neutral domina demasiado
    neutral_pct = dist['neutral'] / len(labels) * 100
    if neutral_pct > 70:
        print(f"\n  ⚠️  {neutral_pct:.0f}% neutral — considera bajar --threshold a 1")
    elif neutral_pct < 10:
        print(f"\n  ⚠️  Solo {neutral_pct:.0f}% neutral — considera subir --threshold a 3")

    # ------------------------------------------------------------------
    # PASO 3: Guardar CSV
    # ------------------------------------------------------------------
    print(f"\n[3/3] Guardando en {output_path}")
    output_df = pd.DataFrame({
        'text': texts_clean,
        'label': labels,
        'label_id': label_ids,
        'score_depression': dep_scores,
        'score_anxiety': anx_scores,
    })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_path, index=False)

    print(f"\n✅ Dataset guardado: {output_path}  ({len(output_df)} ejemplos)")
    print(f"\n   Siguiente paso: python scripts/train.py")
    print("=" * 70)


if __name__ == '__main__':
    main()
