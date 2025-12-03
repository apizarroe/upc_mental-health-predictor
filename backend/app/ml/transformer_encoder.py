"""
Encoder Transformer para convertir texto en embeddings vectoriales.
Soporta modelos BERT, RoBERTa y otros transformers de Hugging Face.
"""

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from typing import List
from tqdm import tqdm


class TransformerEncoder:
    """Codificador Transformer para extraer embeddings de texto."""

    def __init__(
        self,
        model_name: str = "PlanTL-GOB-ES/roberta-base-biomedical-es",
        max_length: int = 512,
        batch_size: int = 16,
        device: str = None
    ):
        """
        Inicializa el encoder Transformer.

        Args:
            model_name: Nombre del modelo Transformer a usar (BERT, RoBERTa, etc.)
            max_length: Longitud máxima de tokens
            batch_size: Tamaño del batch para procesamiento
            device: Dispositivo (cuda/cpu), auto-detecta si es None
        """
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size

        # Auto-detectar dispositivo
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        print(f"🔧 Inicializando Transformer Encoder...")
        print(f"   • Modelo: {model_name}")
        print(f"   • Dispositivo: {self.device}")
        print(f"   • Max length: {max_length}")

        # Cargar tokenizer y modelo
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Usar safetensors para evitar vulnerabilidad CVE-2025-32434 en torch.load
        self.model = AutoModel.from_pretrained(
            model_name,
            use_safetensors=True  # Forzar uso de safetensors
        )
        self.model.to(self.device)
        self.model.eval()  # Modo evaluación

        print("✅ Modelo Transformer cargado exitosamente!")

    def encode_texts(
        self,
        texts: List[str],
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Codifica una lista de textos en embeddings BERT.

        Args:
            texts: Lista de textos a codificar
            show_progress: Mostrar barra de progreso

        Returns:
            Array numpy con embeddings (shape: [n_samples, embedding_dim])
        """
        embeddings = []

        # Procesar en batches
        n_batches = (len(texts) + self.batch_size - 1) // self.batch_size

        iterator = range(0, len(texts), self.batch_size)
        if show_progress:
            iterator = tqdm(
                iterator,
                desc="Generando embeddings",
                total=n_batches
            )

        with torch.no_grad():
            for i in iterator:
                batch_texts = texts[i:i + self.batch_size]

                # Tokenizar batch
                encoded = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors='pt'
                )

                # Mover a dispositivo
                input_ids = encoded['input_ids'].to(self.device)
                attention_mask = encoded['attention_mask'].to(self.device)

                # Obtener embeddings
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )

                # Usar [CLS] token embedding (primera posición)
                cls_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()

                embeddings.append(cls_embeddings)

        # Concatenar todos los embeddings
        all_embeddings = np.vstack(embeddings)

        print(f"\n✅ Generados {len(all_embeddings)} embeddings")
        print(f"   • Dimensión: {all_embeddings.shape[1]}")

        return all_embeddings

    def encode_single(self, text: str) -> np.ndarray:
        """
        Codifica un solo texto (útil para predicción).

        Args:
            text: Texto a codificar

        Returns:
            Array numpy con embedding (shape: [embedding_dim])
        """
        embedding = self.encode_texts([text], show_progress=False)
        return embedding[0]

    def get_embedding_dim(self) -> int:
        """
        Retorna la dimensión de los embeddings.

        Returns:
            Dimensión de los embeddings
        """
        return self.model.config.hidden_size


if __name__ == "__main__":
    # Ejemplo de uso
    encoder = TransformerEncoder()

    # Textos de ejemplo
    texts = [
        "Me siento muy triste y sin energía últimamente",
        "El trabajo me causa mucho estrés y ansiedad",
        "Hoy tuve un buen día, salí a caminar"
    ]

    # Generar embeddings
    embeddings = encoder.encode_texts(texts)

    print(f"\nEjemplo de embedding:")
    print(f"  Shape: {embeddings.shape}")
    print(f"  Primeros 5 valores: {embeddings[0][:5]}")
