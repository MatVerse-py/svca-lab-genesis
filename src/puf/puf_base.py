"""
PUF Protocol - Interface base para Physical Unclonable Functions
"""

from typing import Protocol, Optional
from dataclasses import dataclass


@dataclass
class PUFResponse:
    """Resposta de um PUF com metadados"""
    
    response: bytes
    """Resposta bruta do PUF (com ruído)"""
    
    entropy_bits: float
    """Entropia estimada em bits"""
    
    bit_error_rate: float
    """Taxa de erro de bit (BER) estimada"""
    
    challenge: Optional[bytes] = None
    """Challenge usado (se aplicável)"""


class PUFProtocol(Protocol):
    """
    Interface para Physical Unclonable Function
    
    Um PUF é um primitivo físico que gera respostas únicas baseadas
    em variações microscópicas do hardware. Propriedades essenciais:
    
    1. Incopiabilidade: Impossível clonar fisicamente
    2. Imprevisibilidade: Resposta não pode ser prevista
    3. Unicidade: Cada instância é única
    4. Robustez: Resposta estável sob condições normais
    5. Variabilidade: Ruído natural introduz variação
    """
    
    def generate(self, challenge: Optional[bytes] = None) -> PUFResponse:
        """
        Gera resposta PUF para um challenge (ou estado físico atual)
        
        Args:
            challenge: Challenge opcional (para PUFs challenge-response)
        
        Returns:
            PUFResponse com resposta bruta e metadados
        """
        ...
    
    def get_entropy(self) -> float:
        """
        Retorna entropia estimada do PUF em bits
        
        Requisito CORE B DAY: entropia física ≥ 128 bits
        
        Returns:
            Entropia em bits
        """
        ...
    
    def get_ber(self) -> float:
        """
        Retorna taxa de erro de bit (BER) estimada
        
        BER afeta a entropia útil:
        H_extract = n · (1 − 2·BER)² · (1 − I(X;Y))
        
        Returns:
            BER entre 0.0 e 0.5
        """
        ...
    
    def get_id(self) -> str:
        """
        Retorna identificador único do PUF
        
        Returns:
            ID em formato hexadecimal
        """
        ...
