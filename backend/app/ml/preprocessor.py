"""
Preprocesador de texto para conversaciones de salud mental.
Extrae y limpia el texto de las conversaciones para el modelo BERT.
Soporta detección multi-etiqueta (depresión y ansiedad).
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Union

from .text_processing import clean_text as _clean_text


class TextPreprocessor:
    """Preprocesa conversaciones de chat para análisis de trastornos mentales."""

    def __init__(self):
        """Inicializa el preprocesador con keywords para cada trastorno."""
        # Keywords específicas para depresión
        self.depression_keywords = [
            'triste', 'deprimido', 'depresión', 'desesperanza', 'desesperado',
            'vacío', 'soledad', 'solo', 'aislado', 'llorar', 'lloro',
            'culpa', 'inútil', 'fracaso', 'muerte', 'morir', 'suicidio',
            'cansado', 'agotado', 'fatiga', 'poca energía', 'falta energía',
            'motivación'
            # 'sad', 'depressed', 'depression', 'hopeless', 'desperate',
            # 'empty', 'lonely', 'alone', 'isolated', 'cry', 'crying',
            # 'guilt', 'worthless', 'failure', 'death', 'die',
            # 'tired', 'exhausted', 'fatigue', 'energy', 'motivation'
        ]

        # Keywords específicas para ansiedad
        self.anxiety_keywords = [
            'ansiedad', 'ansioso', 'nervioso', 'nerviosismo', 'pánico',
            'preocupado', 'preocupación', 'miedo', 'temor', 'fobia',
            'tensión', 'tenso', 'inquieto', 'agitado', 'estrés', 'estresado',
            'palpitaciones', 'sudor', 'temblor', 'respiración', 'abrumado',
            'insomnio', 'lograr dormir'
            # 'anxiety', 'anxious', 'nervous', 'nervousness', 'panic',
            # 'worried', 'worry', 'fear', 'phobia',
            # 'tension', 'tense', 'restless', 'agitated', 'stress', 'stressed',
            # 'palpitations', 'sweat', 'trembling', 'breathing', 'overwhelmed',
            # 'insomnia', 'sleep'
        ]

    def load_parquet(self, file_path: str) -> pd.DataFrame:
        """
        Carga el archivo parquet con las conversaciones.

        Args:
            file_path: Ruta al archivo parquet

        Returns:
            DataFrame con las conversaciones
        """
        df = pd.read_parquet(file_path)
        print(f"✅ Cargadas {len(df)} conversaciones desde {file_path}")
        return df

    def extract_user_messages(self, conversation: List[Dict]) -> str:
        """
        Extrae solo los mensajes del usuario de una conversación.

        Args:
            conversation: Lista de mensajes con roles y contenido

        Returns:
            String con todos los mensajes del usuario concatenados
        """
        user_messages = [
            msg['content']
            for msg in conversation
            if msg.get('role') == 'user'
        ]
        return ' '.join(user_messages)

    def clean_text(self, text: str) -> str:
        """
        Limpia el texto eliminando caracteres especiales y normalizando espacios.
        Delega a la función centralizada en text_processing.

        Args:
            text: Texto a limpiar

        Returns:
            Texto limpio
        """
        return _clean_text(text)

    def _detect_condition_indicators(
        self,
        text: str,
        keywords: List[str],
        threshold: int = 2
    ) -> int:
        """
        Detecta indicadores de una condición en el texto usando keywords.

        Args:
            text: Texto a analizar
            keywords: Lista de keywords a buscar
            threshold: Número mínimo de keywords para considerar positivo

        Returns:
            1 si detecta indicadores (>= threshold keywords), 0 si no
        """
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
        return 1 if keyword_count >= threshold else 0

    def detect_depression_indicators(self, text: str) -> int:
        """
        Detecta indicadores de depresión en el texto usando keywords.

        Args:
            text: Texto a analizar

        Returns:
            1 si detecta indicadores de depresión, 0 si no
        """
        return self._detect_condition_indicators(text, self.depression_keywords)

    def detect_anxiety_indicators(self, text: str) -> int:
        """
        Detecta indicadores de ansiedad en el texto usando keywords.

        Args:
            text: Texto a analizar

        Returns:
            1 si detecta indicadores de ansiedad, 0 si no
        """
        return self._detect_condition_indicators(text, self.anxiety_keywords)

    def detect_multi_label(self, text: str) -> List[int]:
        """
        Detecta múltiples indicadores (depresión y ansiedad) en el texto.

        Args:
            text: Texto a analizar

        Returns:
            Lista [depression, anxiety] con valores 0 o 1
        """
        depression = self.detect_depression_indicators(text)
        anxiety = self.detect_anxiety_indicators(text)
        return [depression, anxiety]

    def get_matched_keywords(self, text: str) -> Dict[str, List[str]]:
        """
        Retorna las keywords encontradas para cada trastorno.

        Args:
            text: Texto a analizar

        Returns:
            Diccionario con keywords encontradas por trastorno
        """
        text_lower = text.lower()

        depression_matches = [
            kw for kw in self.depression_keywords if kw in text_lower
        ]
        anxiety_matches = [
            kw for kw in self.anxiety_keywords if kw in text_lower
        ]

        return {
            'depression': depression_matches,
            'anxiety': anxiety_matches
        }

    def process_conversations(
        self,
        df: pd.DataFrame,
        multi_label: bool = False
    ) -> Tuple[List[str], Union[List[int], np.ndarray]]:
        """
        Procesa todas las conversaciones del DataFrame.

        Args:
            df: DataFrame con columna 'chat' conteniendo conversaciones
            multi_label: Si True, retorna etiquetas multi-label [dep, anx]

        Returns:
            Tupla de (textos procesados, etiquetas)
            - Si multi_label=False: etiquetas es List[int] (solo depresión)
            - Si multi_label=True: etiquetas es np.ndarray shape (N, 2)
        """
        texts = []
        labels = []

        for idx, row in df.iterrows():
            conversation = row['chat']

            # Extraer mensajes del usuario
            user_text = self.extract_user_messages(conversation)

            # Limpiar texto
            cleaned_text = self.clean_text(user_text)

            # Detectar indicadores
            if multi_label:
                label = self.detect_multi_label(cleaned_text)
            else:
                label = self.detect_depression_indicators(cleaned_text)

            texts.append(cleaned_text)
            labels.append(label)

            if (idx + 1) % 100 == 0:
                print(f"Procesadas {idx + 1}/{len(df)} conversaciones...")

        print(f"\n✅ Total procesado: {len(texts)} conversaciones")

        if multi_label:
            labels_array = np.array(labels)
            depression_count = labels_array[:, 0].sum()
            anxiety_count = labels_array[:, 1].sum()
            both_count = ((labels_array[:, 0] == 1) & (labels_array[:, 1] == 1)).sum()
            neither_count = ((labels_array[:, 0] == 0) & (labels_array[:, 1] == 0)).sum()

            print(f"   📊 Distribución de etiquetas:")
            print(f"   • Solo Depresión: {depression_count - both_count} ({(depression_count - both_count)/len(labels)*100:.1f}%)")
            print(f"   • Solo Ansiedad: {anxiety_count - both_count} ({(anxiety_count - both_count)/len(labels)*100:.1f}%)")
            print(f"   • Ambos: {both_count} ({both_count/len(labels)*100:.1f}%)")
            print(f"   • Ninguno: {neither_count} ({neither_count/len(labels)*100:.1f}%)")

            return texts, labels_array
        else:
            print(f"   • Con indicadores de depresión: {sum(labels)}")
            print(f"   • Sin indicadores: {len(labels) - sum(labels)}")
            return texts, labels

    def create_dataset(
        self,
        file_path: str,
        multi_label: bool = False
    ) -> Tuple[List[str], Union[List[int], np.ndarray]]:
        """
        Pipeline completo: carga y procesa el dataset.

        Args:
            file_path: Ruta al archivo parquet
            multi_label: Si True, retorna etiquetas multi-label [dep, anx]

        Returns:
            Tupla de (textos, etiquetas)
        """
        print("🔄 Iniciando procesamiento del dataset...")

        # Cargar datos
        df = self.load_parquet(file_path)

        # Procesar conversaciones
        texts, labels = self.process_conversations(df, multi_label=multi_label)

        print("\n✅ Dataset preparado exitosamente!")

        return texts, labels


if __name__ == "__main__":
    # Ejemplo de uso
    preprocessor = TextPreprocessor()

    file_path = "../../data/datasets/train-00000-of-00001.parquet"

    # Ejemplo con etiquetas simples (solo depresión)
    print("\n" + "=" * 60)
    print("📝 MODO SIMPLE (solo depresión)")
    print("=" * 60)
    texts, labels = preprocessor.create_dataset(file_path, multi_label=False)
    print(f"Texto: {texts[0][:100]}...")
    print(f"Etiqueta (depresión): {labels[0]}")

    # Ejemplo con multi-label
    print("\n" + "=" * 60)
    print("📝 MODO MULTI-ETIQUETA (depresión + ansiedad)")
    print("=" * 60)
    texts, labels = preprocessor.create_dataset(file_path, multi_label=True)
    print(f"Texto: {texts[0][:100]}...")
    print(f"Etiquetas [depresión, ansiedad]: {labels[0]}")
