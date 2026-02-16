"""
Fuzzy Extractor Module

Implementa extração de chaves criptográficas estáveis de fontes ruidosas (PUF).

Baseado em códigos de correção de erro (BCH) para reconstruir chave
mesmo com variações na resposta do PUF.

Referência CORE B DAY:
H_extract = n · (1 − 2·BER)² · (1 − I(X;Y))
"""

from .fuzzy_extractor import FuzzyExtractor
from .bch_helper import BCHHelper

__all__ = [
    "FuzzyExtractor",
    "BCHHelper",
]
