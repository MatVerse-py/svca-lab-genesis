"""
Ohash Module - Sistema de identidade pública auditável

Implementa Ohash (Origin Hash) para criar identidade pública
eterna e auditável em ledger.

Propriedades CORE B DAY:
- Público
- Eterno
- Auditável
- Imutável
- Perdeu o chip = perdeu a identidade para sempre
"""

from .ohash import Ohash, OhashRecord

__all__ = [
    "Ohash",
    "OhashRecord",
]
