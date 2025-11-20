"""
Loader para datos en formato Parquet con conversaciones JSON.
Formato específico del dataset actual.
"""

import pandas as pd
from typing import List, Dict
from pathlib import Path


class ParquetChatLoader:
    """Carga conversaciones desde archivo Parquet."""

    def __init__(self, file_path: str):
        """
        Inicializa el loader.

        Args:
            file_path: Ruta al archivo parquet
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    def load(self) -> pd.DataFrame:
        """
        Carga el archivo parquet.

        Returns:
            DataFrame con las conversaciones
        """
        df = pd.read_parquet(self.file_path)
        print(f"✅ Cargadas {len(df)} conversaciones desde {self.file_path.name}")
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

    def extract_all_texts(self) -> List[str]:
        """
        Extrae todos los textos de usuario del dataset.

        Returns:
            Lista de textos (uno por conversación)
        """
        df = self.load()
        texts = []

        for idx, row in df.iterrows():
            conversation = row['chat']
            user_text = self.extract_user_messages(conversation)
            texts.append(user_text)

            if (idx + 1) % 100 == 0:
                print(f"   Procesadas {idx + 1}/{len(df)} conversaciones...")

        print(f"✅ Extraídos {len(texts)} textos")
        return texts


# Ejemplo de uso
if __name__ == "__main__":
    loader = ParquetChatLoader("../../data/datasets/train-00000-of-00001.parquet")
    texts = loader.extract_all_texts()

    print(f"\n📝 Ejemplo de texto extraído:")
    print(f"   {texts[0][:200]}...")
