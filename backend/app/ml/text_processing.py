"""
Módulo de procesamiento de texto.
Funciones reutilizables para limpiar y normalizar texto.
"""

import re


def clean_text(text: str) -> str:
    """
    Limpia el texto eliminando caracteres especiales y normalizando espacios.

    Args:
        text: Texto a limpiar

    Returns:
        Texto limpio

    Raises:
        TypeError: Si el texto no es un string
    """
    # Validación de entrada
    if text is None:
        return ""
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    if not text.strip():
        return ""

    # Convertir a minúsculas
    text = text.lower()

    # Eliminar URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # Eliminar emails
    text = re.sub(r'\S+@\S+', '', text)

    # Normalizar espacios múltiples
    text = re.sub(r'\s+', ' ', text)

    # Eliminar espacios al inicio y final
    text = text.strip()

    return text
