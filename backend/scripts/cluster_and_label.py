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
