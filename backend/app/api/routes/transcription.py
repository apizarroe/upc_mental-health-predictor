"""
Endpoints para transcripción de audio a texto.

Este módulo proporciona endpoints para recibir audio y transcribirlo a texto
usando Whisper.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.services.transcription import get_transcription_service
import logging

# Configurar logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...)
):
    """
    Transcribe un archivo de audio a texto.

    Args:
        audio: Archivo de audio (WebM, MP3, WAV, etc.)

    Returns:
        JSON con la transcripción del audio

    Raises:
        HTTPException: Si hay error en la transcripción
    """
    try:
        # Validar que se recibió un archivo
        if not audio:
            raise HTTPException(
                status_code=400,
                detail="No se recibió ningún archivo de audio"
            )

        logger.info(f"Recibido archivo de audio: {audio.filename}")
        logger.info(f"   • Content-type: {audio.content_type}")

        # Leer el contenido del archivo
        audio_data = await audio.read()

        if len(audio_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="El archivo de audio está vacío"
            )

        logger.info(f"   • Tamaño: {len(audio_data)} bytes")

        # Obtener servicio de transcripción
        transcription_service = get_transcription_service()

        # Transcribir audio
        transcription = transcription_service.transcribe_audio(
            audio_data=audio_data,
            language="es"
        )

        if not transcription or len(transcription.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="No se pudo detectar voz en el audio"
            )

        logger.info(f"Transcripción exitosa: {len(transcription)} caracteres")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "transcription": transcription,
                "metadata": {
                    "audio_size_bytes": len(audio_data),
                    "transcription_length": len(transcription),
                    "model_info": transcription_service.get_model_info()
                }
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error al transcribir audio: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el audio: {str(e)}"
        )


@router.get("/transcribe/info")
async def get_transcription_info():
    """
    Obtiene información sobre el servicio de transcripción.

    Returns:
        JSON con información del modelo y configuración
    """
    try:
        transcription_service = get_transcription_service()
        model_info = transcription_service.get_model_info()

        return JSONResponse(
            status_code=200,
            content={
                "status": "available",
                "model": model_info,
                "supported_languages": ["es", "en", "fr", "de", "it", "pt"],
                "supported_formats": ["webm", "mp3", "wav", "m4a", "ogg"]
            }
        )

    except Exception as e:
        logger.error(f"Error al obtener info de transcripción: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )
