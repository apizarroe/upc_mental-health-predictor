"""
Módulo de etiquetado automático.
Detecta indicadores de depresión y otros trastornos usando keywords y reglas.
"""

from typing import List, Dict, Tuple
from enum import Enum


class MentalHealthLabel(Enum):
    """Etiquetas de salud mental."""
    NO_INDICATORS = 0
    DEPRESSION = 1
    ANXIETY = 2
    BOTH = 3


class DepressionDetector:
    """Detector de indicadores de depresión usando keywords."""

    def __init__(self, threshold: int = 2):
        """
        Inicializa el detector.

        Args:
            threshold: Número mínimo de keywords para considerar depresión
        """
        self.threshold = threshold
        self.depression_keywords = {
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

    def detect(self, text: str) -> int:
        """
        Detecta indicadores de depresión en el texto.

        Args:
            text: Texto a analizar (debe estar limpio y en minúsculas)

        Returns:
            1 si detecta indicadores de depresión, 0 si no
        """
        text_lower = text.lower()
        score = sum(w for kw, w in self.depression_keywords.items() if kw in text_lower)
        return 1 if score >= self.threshold else 0

    def get_matched_keywords(self, text: str) -> List[str]:
        text_lower = text.lower()
        return [kw for kw in self.depression_keywords if kw in text_lower]

    def detect_with_confidence(self, text: str) -> Tuple[int, float]:
        text_lower = text.lower()
        score = sum(w for kw, w in self.depression_keywords.items() if kw in text_lower)
        confidence = min(score / (self.threshold * 2), 1.0)
        return 1 if score >= self.threshold else 0, confidence


class AnxietyDetector:
    """Detector de indicadores de ansiedad usando keywords."""

    def __init__(self, threshold: int = 2):
        """Inicializa el detector de ansiedad."""
        self.threshold = threshold
        self.anxiety_keywords = {
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

    def detect(self, text: str) -> int:
        """Detecta indicadores de ansiedad."""
        text_lower = text.lower()
        score = sum(w for kw, w in self.anxiety_keywords.items() if kw in text_lower)
        return 1 if score >= self.threshold else 0


class MultiLabelDetector:
    """Detector que combina múltiples detectores."""

    def __init__(self):
        """Inicializa todos los detectores."""
        self.depression_detector = DepressionDetector()
        self.anxiety_detector = AnxietyDetector()

    def detect(self, text: str) -> Dict[str, int]:
        """
        Detecta múltiples condiciones.

        Args:
            text: Texto a analizar

        Returns:
            Diccionario con etiquetas para cada condición
        """
        return {
            'depression': self.depression_detector.detect(text),
            'anxiety': self.anxiety_detector.detect(text),
        }

    def get_primary_label(self, text: str) -> int:
        """
        Retorna la etiqueta primaria (para compatibilidad con código existente).

        Args:
            text: Texto a analizar

        Returns:
            1 si hay depresión O ansiedad, 0 si no
        """
        labels = self.detect(text)
        return 1 if any(labels.values()) else 0


# Función de conveniencia para retrocompatibilidad
def detect_depression_indicators(text: str, threshold: int = 2) -> int:
    """
    Función standalone para detectar indicadores de depresión.
    Compatible con el código existente.

    Args:
        text: Texto a analizar
        threshold: Número mínimo de keywords

    Returns:
        1 si detecta indicadores, 0 si no
    """
    detector = DepressionDetector(threshold=threshold)
    return detector.detect(text)


# Ejemplo de uso
if __name__ == "__main__":
    # Test básico
    detector = DepressionDetector()

    # Caso con depresión
    text1 = "me siento muy triste y sin energía últimamente"
    label1 = detector.detect(text1)
    keywords1 = detector.get_matched_keywords(text1)
    print(f"Texto: {text1}")
    print(f"Etiqueta: {label1}")
    print(f"Keywords: {keywords1}\n")

    # Caso sin depresión
    text2 = "estoy emocionado por mi nuevo trabajo"
    label2 = detector.detect(text2)
    keywords2 = detector.get_matched_keywords(text2)
    print(f"Texto: {text2}")
    print(f"Etiqueta: {label2}")
    print(f"Keywords: {keywords2}\n")

    # Multi-label
    multi_detector = MultiLabelDetector()
    text3 = "tengo mucha ansiedad y me siento deprimido"
    labels3 = multi_detector.detect(text3)
    print(f"Texto: {text3}")
    print(f"Etiquetas múltiples: {labels3}")
