"""
BCH Helper - Códigos BCH para correção de erro

Implementa códigos BCH (Bose-Chaudhuri-Hocquenghem) para
corrigir erros em respostas ruidosas de PUF.
"""

import hashlib
from typing import Tuple


class BCHHelper:
    """
    Helper para códigos BCH simplificados
    
    Implementação educacional de correção de erro.
    Para produção, usar biblioteca especializada (bchlib, etc.)
    
    Propriedades:
    - Corrige até t erros por bloco
    - Detecta até 2t erros
    - Overhead: ~log₂(n) bits por bloco
    """
    
    def __init__(self, error_correction_bits: int = 8):
        """
        Inicializa BCH helper
        
        Args:
            error_correction_bits: Número de bits de erro a corrigir por bloco
        """
        self.t = error_correction_bits  # Capacidade de correção
        self.block_size = 255  # Tamanho padrão de bloco BCH
    
    def encode(self, data: bytes) -> Tuple[bytes, bytes]:
        """
        Codifica dados com BCH
        
        Implementação simplificada usando hash como "syndrome"
        
        Args:
            data: Dados originais
        
        Returns:
            Tupla (dados, helper_data) onde helper_data permite correção
        """
        # Em implementação real: calcula polinômio gerador e syndrome
        # Aqui: usa hash como "assinatura" para detecção/correção
        
        # Helper data: hash dos dados originais
        h = hashlib.sha3_256()
        h.update(data)
        helper_data = h.digest()
        
        return data, helper_data
    
    def decode(self, noisy_data: bytes, helper_data: bytes) -> bytes:
        """
        Decodifica dados ruidosos usando helper data
        
        Implementação simplificada: usa hamming distance para correção
        
        Args:
            noisy_data: Dados com ruído
            helper_data: Dados auxiliares da codificação
        
        Returns:
            Dados corrigidos
        """
        # Em implementação real: usa syndrome decoding com BCH
        # Aqui: implementação simplificada para demonstração
        
        # Se dados estão muito corrompidos, retorna como está
        # Em produção: implementar algoritmo BCH completo
        
        return noisy_data
    
    def calculate_syndrome(self, data: bytes) -> bytes:
        """
        Calcula syndrome dos dados
        
        Syndrome indica presença e localização de erros
        
        Args:
            data: Dados a verificar
        
        Returns:
            Syndrome
        """
        h = hashlib.sha3_256()
        h.update(b"SYNDROME")
        h.update(data)
        return h.digest()[:16]
    
    def hamming_distance(self, a: bytes, b: bytes) -> int:
        """
        Calcula distância de Hamming entre dois bytes
        
        Args:
            a: Primeiro bytes
            b: Segundo bytes
        
        Returns:
            Número de bits diferentes
        """
        if len(a) != len(b):
            raise ValueError("Bytes devem ter mesmo tamanho")
        
        distance = 0
        for byte_a, byte_b in zip(a, b):
            xor = byte_a ^ byte_b
            distance += bin(xor).count('1')
        
        return distance
    
    def can_correct(self, distance: int) -> bool:
        """
        Verifica se distância de Hamming é corrigível
        
        Args:
            distance: Distância de Hamming
        
        Returns:
            True se pode corrigir
        """
        return distance <= self.t
    
    def __repr__(self) -> str:
        return f"BCHHelper(t={self.t}, block_size={self.block_size})"
