"""
Módulo de procesamiento de texto.
Funciones reutilizables para limpiar y normalizar texto.
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Limpia el texto eliminando caracteres especiales y normalizando espacios.

    Args:
        text: Texto a limpiar

    Returns:
        Texto limpio
    """
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


def batch_clean_texts(texts: List[str]) -> List[str]:
    """
    Limpia múltiples textos en batch.

    Args:
        texts: Lista de textos a limpiar

    Returns:
        Lista de textos limpios
    """
    return [clean_text(text) for text in texts]


def remove_special_characters(text: str, keep_chars: str = '') -> str:
    """
    Elimina caracteres especiales, opcionalmente manteniendo algunos.

    Args:
        text: Texto a procesar
        keep_chars: Caracteres especiales a mantener (ej: ".,!?")

    Returns:
        Texto sin caracteres especiales
    """
    pattern = f'[^a-záéíóúñü0-9\\s{re.escape(keep_chars)}]'
    return re.sub(pattern, '', text, flags=re.IGNORECASE)


def normalize_whitespace(text: str) -> str:
    """
    Normaliza espacios en blanco.

    Args:
        text: Texto a normalizar

    Returns:
        Texto con espacios normalizados
    """
    # Reemplazar múltiples espacios con uno solo
    text = re.sub(r'\s+', ' ', text)
    # Eliminar espacios al inicio y final
    return text.strip()
