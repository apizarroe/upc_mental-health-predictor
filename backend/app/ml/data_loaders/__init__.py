"""
Data loaders para diferentes formatos de entrada.
Cada loader retorna una lista de textos listos para procesar.
"""

from .parquet_loader import ParquetChatLoader
from .csv_loader import CSVTextLoader, CSVPatientLoader

__all__ = ['ParquetChatLoader', 'CSVTextLoader', 'CSVPatientLoader']
