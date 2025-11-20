"""
Preprocesador de texto para conversaciones de salud mental.
Extrae y limpia el texto de las conversaciones para el modelo BERT.
"""

import pandas as pd
import re
from typing import List, Dict, Tuple


class TextPreprocessor:
    """Preprocesa conversaciones de chat para análisis de depresión."""

    def __init__(self):
        """Inicializa el preprocesador."""
        self.depression_keywords = [
            'triste', 'deprimido', 'ansiedad', 'estrés', 'abrumado',
            'soledad', 'desesperanza', 'cansado', 'agotado', 'insomnio',
            'sad', 'depressed', 'anxiety', 'stress', 'overwhelmed',
            'lonely', 'hopeless', 'tired', 'exhausted', 'insomnia'
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

    def detect_depression_indicators(self, text: str) -> int:
        """
        Detecta indicadores de depresión en el texto usando keywords.
        Esta es una etiqueta inicial simple que puede refinarse.

        Args:
            text: Texto a analizar

        Returns:
            1 si detecta indicadores de depresión, 0 si no
        """
        text_lower = text.lower()

        # Contar keywords de depresión
        keyword_count = sum(
            1 for keyword in self.depression_keywords
            if keyword in text_lower
        )

        # Si encuentra 2 o más keywords, considera que hay indicadores
        return 1 if keyword_count >= 2 else 0

    def process_conversations(
        self,
        df: pd.DataFrame
    ) -> Tuple[List[str], List[int]]:
        """
        Procesa todas las conversaciones del DataFrame.

        Args:
            df: DataFrame con columna 'chat' conteniendo conversaciones

        Returns:
            Tupla de (textos procesados, etiquetas de depresión)
        """
        texts = []
        labels = []

        for idx, row in df.iterrows():
            conversation = row['chat']

            # Extraer mensajes del usuario
            user_text = self.extract_user_messages(conversation)

            # Limpiar texto
            cleaned_text = self.clean_text(user_text)

            # Detectar depresión (etiqueta simple)
            label = self.detect_depression_indicators(cleaned_text)

            texts.append(cleaned_text)
            labels.append(label)

            if (idx + 1) % 100 == 0:
                print(f"Procesadas {idx + 1}/{len(df)} conversaciones...")

        print(f"\n✅ Total procesado: {len(texts)} conversaciones")
        print(f"   • Con indicadores de depresión: {sum(labels)}")
        print(f"   • Sin indicadores: {len(labels) - sum(labels)}")

        return texts, labels

    def create_dataset(
        self,
        file_path: str
    ) -> Tuple[List[str], List[int]]:
        """
        Pipeline completo: carga y procesa el dataset.

        Args:
            file_path: Ruta al archivo parquet

        Returns:
            Tupla de (textos, etiquetas)
        """
        print("🔄 Iniciando procesamiento del dataset...")

        # Cargar datos
        df = self.load_parquet(file_path)

        # Procesar conversaciones
        texts, labels = self.process_conversations(df)

        print("\n✅ Dataset preparado exitosamente!")

        return texts, labels


if __name__ == "__main__":
    # Ejemplo de uso
    preprocessor = TextPreprocessor()

    file_path = "../../data/datasets/train-00000-of-00001.parquet"
    texts, labels = preprocessor.create_dataset(file_path)

    # Mostrar ejemplo
    print("\n📝 Ejemplo de datos procesados:")
    print(f"Texto: {texts[0][:200]}...")
    print(f"Etiqueta (depresión): {labels[0]}")
