"""
Loader para datos en formato CSV.
Solo se encarga de CARGAR textos, NO de etiquetar.
"""

import pandas as pd
from typing import List, Optional
from pathlib import Path


class CSVTextLoader:
    """Carga textos desde archivo CSV."""

    def __init__(
        self,
        file_path: str,
        text_column: str = 'text',
        encoding: str = 'utf-8'
    ):
        """
        Inicializa el loader.

        Args:
            file_path: Ruta al archivo CSV
            text_column: Nombre de la columna con el texto
            encoding: Encoding del archivo
        """
        self.file_path = Path(file_path)
        self.text_column = text_column
        self.encoding = encoding

        if not self.file_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    def load(self) -> pd.DataFrame:
        """
        Carga el archivo CSV.

        Returns:
            DataFrame con los datos
        """
        df = pd.read_csv(self.file_path, encoding=self.encoding)
        print(f"✅ Cargadas {len(df)} filas desde {self.file_path.name}")

        # Validar que existe la columna de texto
        if self.text_column not in df.columns:
            raise ValueError(
                f"Columna '{self.text_column}' no encontrada. "
                f"Columnas disponibles: {list(df.columns)}"
            )

        return df

    def extract_texts(self) -> List[str]:
        """
        Extrae todos los textos del CSV.
        NO realiza etiquetado, solo carga textos crudos.

        Returns:
            Lista de textos sin procesar
        """
        df = self.load()
        texts = df[self.text_column].fillna('').astype(str).tolist()

        print(f"✅ Extraídos {len(texts)} textos desde columna '{self.text_column}'")
        return texts


class CSVPatientLoader:
    """
    Loader especializado para CSV con interacciones de pacientes.
    Agrupa múltiples mensajes por paciente o por paciente+sesión.
    """

    def __init__(
        self,
        file_path: str,
        patient_id_column: str = 'patient_id',
        session_column: Optional[str] = None,
        message_column: str = 'message',
        timestamp_column: Optional[str] = None,
        encoding: str = 'utf-8'
    ):
        """
        Inicializa el loader.

        Args:
            file_path: Ruta al archivo CSV
            patient_id_column: Columna con ID del paciente
            session_column: Columna con ID de sesión (opcional)
            message_column: Columna con el mensaje
            timestamp_column: Columna con timestamp (opcional, para ordenar)
            encoding: Encoding del archivo
        """
        self.file_path = Path(file_path)
        self.patient_id_column = patient_id_column
        self.session_column = session_column
        self.message_column = message_column
        self.timestamp_column = timestamp_column
        self.encoding = encoding

        if not self.file_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    def load_grouped_by_patient(self) -> List[str]:
        """
        Carga mensajes agrupados por paciente.
        NO realiza etiquetado, solo agrupa textos.

        Returns:
            Lista de textos (un texto por paciente con todos sus mensajes concatenados)
        """
        df = pd.read_csv(self.file_path, encoding=self.encoding)

        print(f"✅ Cargadas {len(df)} filas desde {self.file_path.name}")

        # Validar columnas
        if self.patient_id_column not in df.columns:
            raise ValueError(f"Columna '{self.patient_id_column}' no encontrada")
        if self.message_column not in df.columns:
            raise ValueError(f"Columna '{self.message_column}' no encontrada")

        # Ordenar por timestamp si existe
        if self.timestamp_column and self.timestamp_column in df.columns:
            df = df.sort_values([self.patient_id_column, self.timestamp_column])

        # Agrupar mensajes por paciente
        grouped = df.groupby(self.patient_id_column)[self.message_column].apply(
            lambda x: ' '.join(x.fillna('').astype(str))
        )

        texts = grouped.tolist()

        print(f"✅ Agrupados mensajes de {len(texts)} pacientes únicos")
        return texts

    def load_grouped_by_session(self) -> List[str]:
        """
        Carga mensajes agrupados por paciente + sesión.
        Requiere que session_column esté configurado.
        NO realiza etiquetado, solo agrupa textos.

        Returns:
            Lista de textos (un texto por sesión con todos sus mensajes concatenados)
        """
        if not self.session_column:
            raise ValueError(
                "session_column debe estar configurado para usar load_grouped_by_session(). "
                "Inicializa el loader con session_column='sesion'"
            )

        df = pd.read_csv(self.file_path, encoding=self.encoding)

        print(f"✅ Cargadas {len(df)} filas desde {self.file_path.name}")

        # Validar columnas
        if self.patient_id_column not in df.columns:
            raise ValueError(f"Columna '{self.patient_id_column}' no encontrada")
        if self.session_column not in df.columns:
            raise ValueError(f"Columna '{self.session_column}' no encontrada")
        if self.message_column not in df.columns:
            raise ValueError(f"Columna '{self.message_column}' no encontrada")

        # Construir columnas de ordenamiento
        sort_columns = [self.patient_id_column, self.session_column]
        if self.timestamp_column and self.timestamp_column in df.columns:
            sort_columns.append(self.timestamp_column)

        df = df.sort_values(sort_columns)

        # Agrupar mensajes por paciente + sesión
        grouped = df.groupby([self.patient_id_column, self.session_column])[self.message_column].apply(
            lambda x: ' '.join(x.fillna('').astype(str))
        )

        texts = grouped.tolist()

        print(f"✅ Agrupados mensajes de {len(texts)} sesiones únicas")
        return texts


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 60)
    print("EJEMPLOS DE USO - CSV LOADERS")
    print("=" * 60)

    print("\n📋 Ejemplo 1: CSV simple con una columna de texto")
    print("-" * 60)
    print("""
# Estructura del CSV:
# text
# "Me siento muy triste últimamente"
# "Estoy emocionado por mi nuevo trabajo"
# "Tengo mucha ansiedad"

from app.ml.data_loaders import CSVTextLoader
from app.ml.text_processing import clean_text
from app.ml.labeling import DepressionDetector

# 1. Cargar textos crudos (SOLO carga)
loader = CSVTextLoader("data.csv", text_column="text")
texts = loader.extract_texts()

# 2. Limpiar textos (módulo independiente - REUTILIZABLE)
clean_texts = [clean_text(t) for t in texts]

# 3. Etiquetar (módulo independiente - REUTILIZABLE)
detector = DepressionDetector()
labels = [detector.detect(t) for t in clean_texts]

# Resultado: texts y labels listos para entrenamiento
    """)

    print("\n👥 Ejemplo 2: CSV con múltiples mensajes por paciente")
    print("-" * 60)
    print("""
# Estructura del CSV:
# patient_id,message,created_at
# PAC001,"Me siento triste",2025-01-01 10:00
# PAC001,"No tengo energía",2025-01-01 10:05
# PAC002,"Estoy emocionado",2025-01-01 11:00

from app.ml.data_loaders import CSVPatientLoader
from app.ml.text_processing import clean_text
from app.ml.labeling import DepressionDetector

# 1. Cargar y agrupar por paciente (SOLO carga y agrupa)
loader = CSVPatientLoader(
    "patient_messages.csv",
    patient_id_column="patient_id",
    message_column="message",
    timestamp_column="created_at"
)
patient_texts = loader.load_grouped_by_patient()
# Resultado: ["Me siento triste No tengo energía", "Estoy emocionado"]

# 2. Limpiar (REUTILIZABLE - funciona con cualquier fuente)
clean_texts = [clean_text(t) for t in patient_texts]

# 3. Etiquetar (REUTILIZABLE - funciona con cualquier fuente)
detector = DepressionDetector()
labels = [detector.detect(t) for t in clean_texts]
    """)

    print("\n" + "=" * 60)
    print("✅ Separación de responsabilidades:")
    print("   • Loaders: Solo cargan textos crudos")
    print("   • text_processing: Solo limpia textos (REUTILIZABLE)")
    print("   • labeling: Solo etiqueta textos (REUTILIZABLE)")
    print("=" * 60)
    print("\n💡 Ventaja: Puedes usar el mismo detector y limpiador")
    print("   con Parquet, CSV, API, JSON, base de datos, etc.")
    print("=" * 60)
