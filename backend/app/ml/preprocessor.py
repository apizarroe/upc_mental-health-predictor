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
        keywords: Dict[str, int],
        threshold: int = 2
    ) -> int:
        """
        Detecta indicadores de una condición usando score ponderado de keywords.

        Args:
            text: Texto a analizar
            keywords: Dict {keyword: peso} donde frases=2, palabras=1
            threshold: Score mínimo ponderado para considerar positivo

        Returns:
            1 si score >= threshold, 0 si no
        """
        text_lower = text.lower()
        score = sum(weight for kw, weight in keywords.items() if kw in text_lower)
        return 1 if score >= threshold else 0

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
