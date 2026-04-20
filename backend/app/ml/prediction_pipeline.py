"""
Pipeline de predicción: MiniLM embeddings + keyword scores + Logistic Regression.
Reemplaza el pipeline anterior BERT-large + XGBoost.
"""

import json
import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

from .text_processing import clean_text

os.environ['TOKENIZERS_PARALLELISM'] = 'false'

BERT_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

DEPRESSION_KEYWORDS = {
    # Frases del dataset real — variantes masculino/femenino (peso 2)
    'me siento muy triste': 2, 'me siento triste': 2,
    'me he sentido muy triste': 2, 'me he sentido triste': 2, 'me he sentido solo': 2, 'me he sentido sola': 2,
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
    # Síntomas físicos y cognitivos de depresión (peso 1)
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
    # Síntomas físicos y cognitivos de ansiedad (peso 1)
    'inquieto': 1, 'inquieta': 1, 'nervioso': 1, 'nerviosa': 1,
    'preocupación': 1, 'tensión': 1, 'sobresaltado': 1, 'sobresaltada': 1,
}

LABEL_MAP = {0: 'depression', 1: 'anxiety', 2: 'neutral'}


def _keyword_score(text: str, keywords: dict) -> float:
    t = text.lower()
    return sum(w for kw, w in keywords.items() if kw in t)


def _matched_keywords(text: str, keywords: dict) -> List[str]:
    t = text.lower()
    return [kw for kw in keywords if kw in t]


class PredictionPipeline:
    """
    Pipeline de predicción: MiniLM + keyword scores → Logistic Regression.
    Carga el modelo .pkl más reciente del directorio de modelos.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        models_dir: str = 'data/trained_models',
        verbose: bool = True,
    ):
        self.verbose = verbose
        self.models_dir = Path(models_dir)
        self.metadata: Dict = {}
        self.model_name: Optional[str] = None

        model_file = Path(model_path) if model_path else self._find_latest_model()
        self._load(model_file)

    def _find_latest_model(self) -> Path:
        if not self.models_dir.exists():
            raise FileNotFoundError(
                f"Directorio de modelos no encontrado: {self.models_dir}\n"
                "Ejecuta: python scripts/cluster_and_label.py && python scripts/train.py"
            )
        candidates = list(self.models_dir.glob('mental_health_lr_*.pkl'))
        if not candidates:
            raise FileNotFoundError(
                f"No se encontró ningún modelo en {self.models_dir}\n"
                "Ejecuta: python scripts/cluster_and_label.py && python scripts/train.py"
            )
        return max(candidates, key=lambda p: p.stat().st_mtime)

    def _load(self, model_file: Path):
        if not model_file.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {model_file}")

        self.model_name = model_file.stem

        metadata_file = model_file.parent / f"{model_file.stem}_metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                self.metadata = json.load(f)

        with open(model_file, 'rb') as f:
            payload = pickle.load(f)

        # Soporte para modelos con par de clasificadores binarios o clasificador único (legacy)
        if isinstance(payload, dict) and 'depression' in payload and 'anxiety' in payload:
            self.clf_depression = payload['depression']
            self.clf_anxiety = payload['anxiety']
            self.classifier = None
        else:
            self.classifier = payload
            self.clf_depression = None
            self.clf_anxiety = None

        self.encoder = SentenceTransformer(BERT_MODEL)

        if self.verbose:
            print(f"Modelo cargado: {model_file.name}")
            if self.metadata:
                m = self.metadata.get('metrics', {})
                print(f"  F1 weighted: {m.get('f1_weighted', 'N/A')}")

    def _build_features(self, texts: List[str], embeddings: np.ndarray) -> np.ndarray:
        dep = np.array([[_keyword_score(t, DEPRESSION_KEYWORDS)] for t in texts])
        anx = np.array([[_keyword_score(t, ANXIETY_KEYWORDS)] for t in texts])
        max_dep = dep.max() or 1
        max_anx = anx.max() or 1
        return np.hstack([embeddings, dep / max_dep, anx / max_anx])

    # Umbrales independientes por condición
    THRESHOLD_DEPRESSION = 0.35
    THRESHOLD_ANXIETY = 0.35

    # Umbrales de decisión — al menos score=2 más señal semántica para activar
    THRESHOLD_DEPRESSION = 0.38
    THRESHOLD_ANXIETY = 0.38

    def _score_to_prob(self, kw_score: float, semantic_boost: float) -> float:
        """Convierte keyword score + señal semántica a probabilidad realista.

        Puntos de referencia con la curva actual:
          score=0  → ~8-12%   (sin keywords, solo contexto semántico leve)
          score=2  → ~38-42%  (una frase de peso 2)
          score=4  → ~62-68%  (frases moderadas)
          score=6  → ~78-83%  (varias frases claras)
          score=10 → ~88-92%  (texto severo, múltiples indicadores)
        """
        import math
        if kw_score == 0:
            # Sin keywords: solo señal semántica muy atenuada
            return max(0.05, min(0.18, 0.08 + 0.10 * semantic_boost))
        # Sigmoide centrada en score=4, temperatura k=0.40
        sigmoid = 1.0 / (1.0 + math.exp(-0.40 * (kw_score - 4.0)))
        # Mezcla 75% keyword-sigmoide + 25% señal semántica
        combined = 0.75 * sigmoid + 0.25 * semantic_boost
        return max(0.20, min(0.92, combined))

    def _predict_proba_pair(self, X: np.ndarray, texts: List[str]):
        """Retorna (prob_depression, prob_anxiety) combinando semántica y keywords."""
        if self.clf_depression is not None:
            sem_dep = float(self.clf_depression.predict_proba(X)[0][1])
            sem_anx = float(self.clf_anxiety.predict_proba(X)[0][1])
        else:
            probas = self.classifier.predict_proba(X)[0]
            sem_dep = float(probas[0])
            sem_anx = float(probas[1])

        kw_dep = _keyword_score(texts[0], DEPRESSION_KEYWORDS)
        kw_anx = _keyword_score(texts[0], ANXIETY_KEYWORDS)

        return self._score_to_prob(kw_dep, sem_dep), self._score_to_prob(kw_anx, sem_anx)
        return prob_depression, prob_anxiety

    def predict_text(self, text: str, return_probabilities: bool = True) -> Dict:
        processed = clean_text(text)
        embedding = self.encoder.encode([processed], convert_to_numpy=True)
        embedding = normalize(embedding)
        X = self._build_features([processed], embedding)

        prob_depression, prob_anxiety = self._predict_proba_pair(X, [processed])

        # Detección independiente por umbral — ambas pueden ser True simultáneamente
        has_depression = prob_depression >= self.THRESHOLD_DEPRESSION
        has_anxiety = prob_anxiety >= self.THRESHOLD_ANXIETY

        result = {
            'text': text,
            'predictions': {
                'depression': {
                    'prediction': int(has_depression),
                    'label': 'Depresión' if has_depression else 'Sin depresión',
                    'threshold': self.THRESHOLD_DEPRESSION,
                },
                'anxiety': {
                    'prediction': int(has_anxiety),
                    'label': 'Ansiedad' if has_anxiety else 'Sin ansiedad',
                    'threshold': self.THRESHOLD_ANXIETY,
                },
            },
            'summary': {
                'has_depression': has_depression,
                'has_anxiety': has_anxiety,
                'conditions_detected': [c for c, v in [('depression', has_depression), ('anxiety', has_anxiety)] if v],
            },
        }

        if return_probabilities:
            result['predictions']['depression']['probability'] = prob_depression
            result['predictions']['depression']['confidence'] = prob_depression
            result['predictions']['anxiety']['probability'] = prob_anxiety
            result['predictions']['anxiety']['confidence'] = prob_anxiety

        return result

    def predict_batch(self, texts: List[str], return_probabilities: bool = True) -> List[Dict]:
        processed = [clean_text(t) for t in texts]
        embeddings = self.encoder.encode(processed, batch_size=32, convert_to_numpy=True)
        embeddings = normalize(embeddings)
        X = self._build_features(processed, embeddings)

        if self.clf_depression is not None:
            all_probas_dep = self.clf_depression.predict_proba(X)
            all_probas_anx = self.clf_anxiety.predict_proba(X)
            all_probas = None
        else:
            all_probas = self.classifier.predict_proba(X)
            all_probas_dep = all_probas_anx = None

        results = []
        for i, text in enumerate(texts):
            if all_probas_dep is not None:
                prob_dep_raw = float(all_probas_dep[i][1])
                prob_anx_raw = float(all_probas_anx[i][1])
            else:
                prob_dep_raw = float(all_probas[i][0])
                prob_anx_raw = float(all_probas[i][1])
            kw_dep = _keyword_score(processed[i], DEPRESSION_KEYWORDS)
            kw_anx = _keyword_score(processed[i], ANXIETY_KEYWORDS)
            prob_depression = self._score_to_prob(kw_dep, prob_dep_raw)
            prob_anxiety = self._score_to_prob(kw_anx, prob_anx_raw)
            has_depression = prob_depression >= self.THRESHOLD_DEPRESSION
            has_anxiety = prob_anxiety >= self.THRESHOLD_ANXIETY

            r = {
                'text': text,
                'predictions': {
                    'depression': {
                        'prediction': int(has_depression),
                        'label': 'Depresión' if has_depression else 'Sin depresión',
                        'threshold': self.THRESHOLD_DEPRESSION,
                    },
                    'anxiety': {
                        'prediction': int(has_anxiety),
                        'label': 'Ansiedad' if has_anxiety else 'Sin ansiedad',
                        'threshold': self.THRESHOLD_ANXIETY,
                    },
                },
                'summary': {
                    'has_depression': has_depression,
                    'has_anxiety': has_anxiety,
                    'conditions_detected': [c for c, v in [('depression', has_depression), ('anxiety', has_anxiety)] if v],
                },
            }
            if return_probabilities:
                r['predictions']['depression']['probability'] = prob_depression
                r['predictions']['depression']['confidence'] = prob_depression
                r['predictions']['anxiety']['probability'] = prob_anxiety
                r['predictions']['anxiety']['confidence'] = prob_anxiety
            results.append(r)

        return results

    def get_model_info(self) -> Dict:
        return {
            'model_name': self.model_name,
            'model_type': self.metadata.get('model_type', 'logistic_regression_multilabel'),
            'labels': self.metadata.get('labels', ['depression', 'anxiety', 'neutral']),
            'bert_model': BERT_MODEL,
            'created_at': self.metadata.get('created_at'),
            'metrics': self.metadata.get('metrics'),
            'metadata_available': bool(self.metadata),
        }

    def is_multilabel_model(self) -> bool:
        return True
