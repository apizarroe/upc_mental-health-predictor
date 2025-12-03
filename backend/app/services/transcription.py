"""
Servicio de transcripción de audio usando Faster Whisper.

Este módulo proporciona funcionalidad para transcribir audio a texto
usando el modelo Whisper optimizado con CTranslate2.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel


class TranscriptionService:
    """
    Servicio de transcripción de audio.

    Utiliza Faster Whisper para transcribir audio a texto de manera eficiente.
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        Inicializa el servicio de transcripción.

        Args:
            model_size: Tamaño del modelo Whisper (tiny, base, small, medium, large)
            device: Dispositivo a usar (cpu, cuda, mps)
            compute_type: Tipo de cómputo (int8, float16, float32)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model: Optional[WhisperModel] = None

        print(f"Inicializando servicio de transcripción...")
        print(f"   • Modelo: whisper-{model_size}")
        print(f"   • Dispositivo: {device}")
        print(f"   • Compute type: {compute_type}")

    @property
    def model(self) -> WhisperModel:
        """
        Obtiene o carga el modelo Whisper (lazy loading).

        Returns:
            Instancia del modelo Whisper
        """
        if self._model is None:
            print(f"Descargando/cargando modelo Whisper-{self.model_size}...")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            print("Modelo Whisper cargado exitosamente")

        return self._model

    def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "es"
    ) -> str:
        """
        Transcribe audio desde bytes.

        Args:
            audio_data: Datos del audio en bytes
            language: Código del idioma (es para español)

        Returns:
            Texto transcrito

        Raises:
            Exception: Si hay error en la transcripción
        """
        # Crear archivo temporal para el audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_path = temp_file.name
            temp_file.write(audio_data)

        try:
            print(f"Transcribiendo audio......")
            print(f"   • Archivo temporal: {temp_path}")
            print(f"   • Tamaño: {len(audio_data)} bytes")

            # Transcribir audio
            segments, info = self.model.transcribe(
                temp_path,
                language=language,
                vad_filter=True,  # Filtro de actividad de voz
                beam_size=5,
            )

            # Obtener idioma detectado
            detected_lang = info.language
            lang_prob = info.language_probability

            print(f"   • Idioma detectado: {detected_lang} (prob: {lang_prob:.2f})")

            # Concatenar todos los segmentos
            transcription = " ".join([segment.text.strip() for segment in segments])

            print(f"✅ Transcripción completada")
            print(f"   • Longitud: {len(transcription)} caracteres")

            return transcription.strip()

        except Exception as e:
            print(f"Error en transcripción: {e}")
            raise Exception(f"Error al transcribir audio: {str(e)}")

        finally:
            # Eliminar archivo temporal
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"No se pudo eliminar archivo temporal: {e}")

    def get_model_info(self) -> dict:
        """
        Obtiene información sobre el modelo de transcripción.

        Returns:
            Diccionario con información del modelo
        """
        return {
            "model_type": "faster-whisper",
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "language": "es",
        }


# Singleton global del servicio de transcripción
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """
    Obtiene la instancia singleton del servicio de transcripción.

    Returns:
        Instancia del servicio de transcripción
    """
    global _transcription_service

    if _transcription_service is None:
        # Obtener configuración del entorno
        device = os.getenv("DEVICE", "cpu").lower()

        # Ajustar compute_type según el dispositivo
        if device == "cuda":
            compute_type = "float16"
        elif device == "mps":
            # MPS no soportado por faster-whisper, usar CPU
            device = "cpu"
            compute_type = "int8"
        else:
            compute_type = "int8"

        _transcription_service = TranscriptionService(
            model_size="base",  # Buen balance entre velocidad y precisión
            device=device,
            compute_type=compute_type
        )

    return _transcription_service
