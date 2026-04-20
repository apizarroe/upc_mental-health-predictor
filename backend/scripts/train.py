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
from sentence_transformers import SentenceTransformer
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

# ---------------------------------------------------------------------------
# Keywords con pesos — deben mantenerse sincronizadas con preprocessor.py
# ---------------------------------------------------------------------------

DEPRESSION_KEYWORDS = {
    # Frases del dataset real — variantes masculino/femenino (peso 2)
    'me siento muy triste': 2, 'me siento triste': 2,
    'me siento tan perdida': 2, 'me siento tan perdido': 2,
    'me siento perdido': 2, 'me siento perdida': 2,
    'siento que ya no': 2, 'siento que no importa': 2,
    'siento que he perdido': 2, 'siento que no soy': 2,
    'no puedo evitar sentirme': 2, 'siento que estoy atrapado': 2,
    'siento que estoy atrapada': 2,
    'ya no sé qué': 2, 'ya no sé cómo': 2,
    'estoy cansado de': 2, 'estoy cansada de': 2,
    'me siento solo': 2, 'me siento sola': 2,
    'me siento vacío': 2, 'me siento vacía': 2,
    'me siento un fracaso': 2, 'no quiero seguir': 2,
    'me siento culpable': 2, 'me siento avergonzado': 2, 'me siento avergonzada': 2,
    'dolor emocional': 2, 'no vale la pena': 2, 'sin esperanza': 2,
    'perdí las ganas': 2, 'me siento invisible': 2,
    'nadie me entiende': 2, 'quisiera desaparecer': 2,
    'me da igual todo': 2, 'todo me cuesta': 2,
    'ya no disfruto': 2, 'no encuentro sentido': 2,
    'siento que no tiene sentido': 2, 'me siento muy sola': 2, 'me siento muy solo': 2,
    # Palabras exclusivas (peso 1)
    'anhedonia': 1, 'desesperanza': 1, 'apatía': 1, 'desgano': 1,
    'melancolía': 1, 'autoculpa': 1, 'abatido': 1, 'abatida': 1,
    'desanimado': 1, 'desanimada': 1, 'hundido': 1, 'hundida': 1,
    'desvalido': 1, 'resignado': 1, 'resignada': 1,
    'decaído': 1, 'decaída': 1, 'letárgico': 1, 'letárgica': 1,
    'agotado': 1, 'agotada': 1, 'sin energía': 1, 'sin fuerzas': 1,
    'sin motivación': 1, 'sin ganas': 1, 'desesperado': 1, 'desesperada': 1,
    'triste': 1, 'tristeza': 1, 'lloro': 1, 'llorar': 1, 'llorando': 1,
    'vacío': 1, 'vacía': 1, 'inútil': 1,
}

ANXIETY_KEYWORDS = {
    # Frases del dataset real — variantes masculino/femenino (peso 2)
    'me siento ansioso': 2, 'me siento ansiosa': 2,
    'me siento muy ansioso': 2, 'me siento muy ansiosa': 2,
    'estoy ansioso': 2, 'estoy ansiosa': 2,
    'constantemente preocupado': 2, 'constantemente preocupada': 2,
    'siento que estoy constantemente': 2,
    'no puedo deshacerme de': 2, 'no puedo evitar sentir': 2,
    'no puedo escapar': 2, 'tengo miedo de que': 2,
    'me siento abrumado': 2, 'me siento abrumada': 2,
    'me siento abrumado por': 2, 'me siento abrumada por': 2,
    'siento que me estoy': 2, 'pensamientos negativos': 2,
    'no puedo concentrarme': 2, 'no puedo dormir': 2,
    'siento que pierdo el control': 2, 'siento que algo malo': 2,
    'mi mente no para': 2, 'no puedo relajarme': 2,
    'me cuesta respirar': 2, 'siento el corazón acelerado': 2,
    'no puedo con tanto': 2, 'todo me genera angustia': 2,
    # Frases de ansiedad laboral/situacional (peso 2)
    'bajo mucha presión': 2, 'bajo una presión': 2,
    'fuente de estrés': 2, 'mucho estrés': 2, 'demasiado estrés': 2,
    'estrés constante': 2, 'constantemente estresado': 2, 'constantemente estresada': 2,
    'no puedo tomar un descanso': 2, 'no puedo descansar': 2,
    'lucha constante': 2, 'siento como si estuviera constantemente': 2,
    'afectando mi bienestar': 2, 'afecta mi salud mental': 2,
    'me resulta difícil': 2, 'difícil mantener el equilibrio': 2,
    # Palabras exclusivas (peso 1)
    'hiperventilación': 1, 'taquicardia': 1, 'rumiación': 1, 'catastrofismo': 1,
    'pánico': 1, 'angustia': 1, 'inquietud': 1, 'hipervigilancia': 1,
    'irritabilidad': 1, 'temor constante': 1, 'ansiedad': 1, 'estrés': 1,
    'inquieto': 1, 'inquieta': 1, 'nervioso': 1, 'nerviosa': 1,
    'preocupación': 1, 'tensión': 1, 'sobresaltado': 1, 'sobresaltada': 1,
}

BERT_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
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
    model = SentenceTransformer(BERT_MODEL)
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True)
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
