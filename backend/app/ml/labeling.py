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
        self.depression_keywords = [
            # Español
            'triste', 'deprimido', 'depresión', 'desesperanza', 'desesperado',
            'vacío', 'soledad', 'solo', 'aislado', 'llorar', 'lloro',
            'culpa', 'inútil', 'fracaso', 'muerte', 'morir', 'suicidio',
            'cansado', 'agotado', 'fatiga', 'energía', 'motivación',
            'insomnio', 'dormir', 'sueño', 'despertar',
            'ansiedad', 'ansioso', 'estrés', 'estresado', 'abrumado',
            'preocupado', 'miedo', 'pánico', 'nervioso',
            # Inglés
            'sad', 'depressed', 'depression', 'hopeless', 'desperate',
            'empty', 'lonely', 'alone', 'isolated', 'cry', 'crying',
            'guilt', 'worthless', 'failure', 'death', 'die', 'suicide',
            'tired', 'exhausted', 'fatigue', 'energy', 'motivation',
            'insomnia', 'sleep', 'wake',
            'anxiety', 'anxious', 'stress', 'stressed', 'overwhelmed',
            'worried', 'fear', 'panic', 'nervous'
        ]

    def detect(self, text: str) -> int:
        """
        Detecta indicadores de depresión en el texto.

        Args:
            text: Texto a analizar (debe estar limpio y en minúsculas)

        Returns:
            1 si detecta indicadores de depresión, 0 si no
        """
        text_lower = text.lower()

        # Contar keywords de depresión
        keyword_count = sum(
            1 for keyword in self.depression_keywords
            if keyword in text_lower
        )

        # Si encuentra >= threshold keywords, considera que hay indicadores
        return 1 if keyword_count >= self.threshold else 0

    def get_matched_keywords(self, text: str) -> List[str]:
        """
        Retorna las keywords encontradas en el texto.

        Args:
            text: Texto a analizar

        Returns:
            Lista de keywords encontradas
        """
        text_lower = text.lower()
        return [
            keyword for keyword in self.depression_keywords
            if keyword in text_lower
        ]

    def detect_with_confidence(self, text: str) -> Tuple[int, float]:
        """
        Detecta depresión y retorna nivel de confianza.

        Args:
            text: Texto a analizar

        Returns:
            Tupla de (etiqueta, confianza 0-1)
        """
        text_lower = text.lower()

        # Contar keywords
        keyword_count = sum(
            1 for keyword in self.depression_keywords
            if keyword in text_lower
        )

        # Calcular confianza (normalizada por número de keywords totales)
        confidence = min(keyword_count / (self.threshold * 2), 1.0)

        label = 1 if keyword_count >= self.threshold else 0

        return label, confidence


class AnxietyDetector:
    """Detector de indicadores de ansiedad usando keywords."""

    def __init__(self, threshold: int = 2):
        """Inicializa el detector de ansiedad."""
        self.threshold = threshold
        self.anxiety_keywords = [
            # Español
            'ansiedad', 'ansioso', 'nervioso', 'nerviosismo', 'pánico',
            'preocupado', 'preocupación', 'miedo', 'temor', 'fobia',
            'tensión', 'tenso', 'inquieto', 'agitado', 'estrés',
            'palpitaciones', 'sudor', 'temblor', 'respiración',
            # Inglés
            'anxiety', 'anxious', 'nervous', 'nervousness', 'panic',
            'worried', 'worry', 'fear', 'phobia',
            'tension', 'tense', 'restless', 'agitated', 'stress',
            'palpitations', 'sweat', 'trembling', 'breathing'
        ]

    def detect(self, text: str) -> int:
        """Detecta indicadores de ansiedad."""
        text_lower = text.lower()
        keyword_count = sum(
            1 for keyword in self.anxiety_keywords
            if keyword in text_lower
        )
        return 1 if keyword_count >= self.threshold else 0


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
