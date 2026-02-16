"""
Physical Unclonable Function (PUF) Module

Implementa funções físicas inclonaveis que geram segredos únicos
baseados em variações físicas microscópicas.
"""

from .puf_base import PUFProtocol
from .simulated_puf import SimulatedPUF
from .optical_puf import OpticalPUF
from .sram_puf import SRAMPUF

__all__ = [
    "PUFProtocol",
    "SimulatedPUF",
    "OpticalPUF",
    "SRAMPUF",
]
