#!/usr/bin/env python3
"""
Script de entrenamiento: MiniLM embeddings + keyword scores + Logistic Regression.

Requiere haber ejecutado antes:
    python scripts/cluster_and_label.py

Uso:
    python scripts/train.py
    python scripts/train.py --data-path data/datasets/labeled_dataset.csv
    python scripts/train.py --output-dir data/trained_models
"""

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import argparse
import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, f1_score, precision_score, recall_score
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.ml.text_processing import clean_text
from app.ml.transformer_encoder import TransformerEncoder
from app.ml.keywords import DEPRESSION_KEYWORDS, ANXIETY_KEYWORDS

BERT_MODEL = 'PlanTL-GOB-ES/roberta-base-biomedical-es'
LABELS = ['depression', 'anxiety', 'neutral']
LABEL_MAP = {'depression': 0, 'anxiety': 1, 'neutral': 2}


def compute_keyword_score(text: str, keywords: dict) -> float:
    text_lower = text.lower()
    return sum(w for kw, w in keywords.items() if kw in text_lower)


def build_features(texts: list[str], embeddings: np.ndarray) -> np.ndarray:
    """Concatena embeddings BERT con keyword scores normalizados."""
    dep_scores = np.array([[compute_keyword_score(t, DEPRESSION_KEYWORDS)] for t in texts])
    anx_scores = np.array([[compute_keyword_score(t, ANXIETY_KEYWORDS)] for t in texts])
    max_dep = dep_scores.max() or 1
    max_anx = anx_scores.max() or 1
    dep_norm = dep_scores / max_dep
    anx_norm = anx_scores / max_anx
    return np.hstack([embeddings, dep_norm, anx_norm])


def main():
    parser = argparse.ArgumentParser(description='Entrenar clasificador de salud mental')
    parser.add_argument('--data-path', default='data/datasets/labeled_dataset.csv')
    parser.add_argument('--output-dir', default='data/trained_models')
    parser.add_argument('--test-size', type=float, default=0.2)
    parser.add_argument('--random-state', type=int, default=42)
    parser.add_argument('--C', type=float, default=1.0, help='Regularización Logistic Regression')
    args = parser.parse_args()

    data_path = backend_dir / args.data_path
    output_dir = backend_dir / args.output_dir

    if not data_path.exists():
        print(f"❌ No se encontró {data_path}")
        print("   Ejecuta primero: python scripts/cluster_and_label.py")
        sys.exit(1)

    print("=" * 70)
    print("ENTRENAMIENTO: MiniLM + Keyword Scores + Logistic Regression")
    print("=" * 70)

    # ------------------------------------------------------------------
    # PASO 1: Cargar dataset etiquetado
    # ------------------------------------------------------------------
    print(f"\n[1/5] Cargando dataset: {data_path}")
    df = pd.read_csv(data_path)
    print(f"      {len(df)} ejemplos cargados")
    print(f"      Distribución:")
    for label, count in df['label'].value_counts().items():
        print(f"        {label:12s}: {count} ({count/len(df)*100:.1f}%)")

    texts = df['text'].fillna('').tolist()
    y = df['label_id'].values

    # ------------------------------------------------------------------
    # PASO 2: Generar embeddings MiniLM
    # ------------------------------------------------------------------
    print(f"\n[2/5] Generando embeddings con {BERT_MODEL}")
    model = TransformerEncoder(BERT_MODEL, batch_size=8)
    embeddings = model.encode_texts(texts)
    embeddings = normalize(embeddings)
    print(f"      Shape: {embeddings.shape}")

    # ------------------------------------------------------------------
    # PASO 3: Construir features (embeddings + keyword scores)
    # ------------------------------------------------------------------
    print(f"\n[3/5] Construyendo features combinadas")
    X = build_features(texts, embeddings)
    print(f"      Shape features: {X.shape}  (embeddings={embeddings.shape[1]}, keyword_scores=2)")

    # ------------------------------------------------------------------
    # PASO 4: Entrenar dos clasificadores binarios independientes
    # ------------------------------------------------------------------
    print(f"\n[4/5] Entrenando clasificadores binarios (C={args.C})")

    # Etiquetas binarias: 1 si es la condición, 0 si no (ansiedad o neutral → 0 para dep_clf)
    y_dep = (df['score_depression'].fillna(0) >= 2).astype(int).values
    y_anx = (df['score_anxiety'].fillna(0) >= 2).astype(int).values

    indices = list(range(len(X)))
    train_idx, test_idx = train_test_split(
        indices, test_size=args.test_size, random_state=args.random_state
    )
    X_train = X[train_idx]
    X_test  = X[test_idx]

    def train_binary(y_all, name):
        y_tr = y_all[train_idx]
        y_te = y_all[test_idx]
        base_clf = LogisticRegression(
            C=args.C, max_iter=1000, random_state=args.random_state,
            class_weight='balanced', solver='lbfgs'
        )
        # Calibración isotónica: corrige probabilidades extremas (0%/100%)
        # cv=5 usa cross-validation interna para aprender la curva de calibración
        clf = CalibratedClassifierCV(base_clf, method='isotonic', cv=5)
        clf.fit(X_train, y_tr)
        pred = clf.predict(X_test)
        f1  = f1_score(y_te, pred, zero_division=0)
        acc = accuracy_score(y_te, pred)
        print(f"  {name}: accuracy={acc:.4f}  F1={f1:.4f}")
        print(classification_report(y_te, pred, target_names=[f'no_{name}', name], zero_division=0))
        return clf, float(f1), float(acc)

    print(f"      Train: {len(train_idx)}  |  Test: {len(test_idx)}")
    clf_dep, f1_dep, acc_dep = train_binary(y_dep, 'depression')
    clf_anx, f1_anx, acc_anx = train_binary(y_anx, 'anxiety')

    # ------------------------------------------------------------------
    # PASO 5: Guardar modelo y metadata
    # ------------------------------------------------------------------
    print(f"[5/5] Guardando modelo")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_filename = f"mental_health_lr_{timestamp}.pkl"
    metadata_filename = f"mental_health_lr_{timestamp}_metadata.json"

    model_path = output_dir / model_filename
    metadata_path = output_dir / metadata_filename

    # Guardamos los dos clasificadores juntos en un dict
    with open(model_path, 'wb') as f:
        pickle.dump({'depression': clf_dep, 'anxiety': clf_anx}, f)

    metadata = {
        'model_type': 'logistic_regression_binary_pair',
        'bert_model': BERT_MODEL,
        'labels': LABELS,
        'label_map': LABEL_MAP,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'training_samples': len(train_idx),
        'test_samples': len(test_idx),
        'hyperparams': {'C': args.C, 'class_weight': 'balanced', 'solver': 'lbfgs'},
        'feature_dim': X.shape[1],
        'embedding_dim': embeddings.shape[1],
        'metrics': {
            'f1_depression': f1_dep,
            'f1_anxiety': f1_anx,
            'f1_weighted': (f1_dep + f1_anx) / 2,
            'accuracy_depression': acc_dep,
            'accuracy_anxiety': acc_anx,
        },
    }
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n  Modelo:   {model_path}")
    print(f"  Metadata: {metadata_path}")

    print("\n" + "=" * 70)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("=" * 70)
    print(f"  F1 depression: {f1_dep:.4f}")
    print(f"  F1 anxiety:    {f1_anx:.4f}")
    print(f"\n  Siguiente paso: iniciar la API")
    print(f"  El modelo nuevo se cargará automáticamente (es el más reciente)")
    print("=" * 70)


if __name__ == '__main__':
    main()
