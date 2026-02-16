"""
Simulated PUF - Implementação simulada de PUF para testes

Simula comportamento de um PUF real usando PRNG criptográfico
com ruído controlado para emular variações físicas.
"""

import hashlib
import secrets
from typing import Optional
from .puf_base import PUFResponse


class SimulatedPUF:
    """
    PUF simulado para testes e desenvolvimento
    
    Simula propriedades de um PUF real:
    - Resposta única baseada em "seed física" (simulada)
    - Ruído controlado para emular variações
    - Entropia configurável
    - BER configurável
    
    AVISO: Não usar em produção! Apenas para testes.
    """
    
    def __init__(
        self,
        seed: Optional[int] = None,
        entropy_bits: float = 256.0,
        ber: float = 0.02,
        response_size: int = 32
    ):
        """
        Inicializa PUF simulado
        
        Args:
            seed: Seed para PRNG (simula "identidade física")
            entropy_bits: Entropia simulada em bits
            ber: Taxa de erro de bit simulada (0.0 a 0.5)
            response_size: Tamanho da resposta em bytes
        """
        if seed is None:
            seed = secrets.randbits(256)
        
        self.seed = seed
        self.entropy_bits = entropy_bits
        self.ber = max(0.0, min(0.5, ber))  # Limita entre 0 e 0.5
        self.response_size = response_size
        
        # Gera "identidade física" única do PUF
        self.puf_id = hashlib.sha3_256(seed.to_bytes(32, 'big')).hexdigest()[:16]
        
        # Estado interno (simula variações físicas)
        self._internal_state = self._generate_internal_state()
    
    def _generate_internal_state(self) -> bytes:
        """Gera estado interno único baseado na seed"""
        h = hashlib.sha3_256()
        h.update(b"SVCA_PUF_INTERNAL_STATE")
        h.update(self.seed.to_bytes(32, 'big'))
        return h.digest()
    
    def _add_noise(self, data: bytes) -> bytes:
        """
        Adiciona ruído à resposta para simular variações físicas
        
        Args:
            data: Dados originais
        
        Returns:
            Dados com ruído aplicado
        """
        if self.ber == 0.0:
            return data
        
        # Converte para bits
        bits = int.from_bytes(data, 'big')
        total_bits = len(data) * 8
        
        # Calcula número de bits a flipar
        num_flips = int(total_bits * self.ber)
        
        # Flipa bits aleatórios
        for _ in range(num_flips):
            bit_pos = secrets.randbelow(total_bits)
            bits ^= (1 << bit_pos)
        
        # Converte de volta para bytes
        return bits.to_bytes(len(data), 'big')
    
    def generate(self, challenge: Optional[bytes] = None) -> PUFResponse:
        """
        Gera resposta PUF
        
        Args:
            challenge: Challenge opcional
        
        Returns:
            PUFResponse com resposta e metadados
        """
        # Cria hash combinando estado interno e challenge
        h = hashlib.sha3_256()
        h.update(self._internal_state)
        
        if challenge is not None:
            h.update(challenge)
        else:
            # Usa timestamp simulado se não houver challenge
            h.update(b"DEFAULT_CHALLENGE")
        
        # Gera resposta base
        response_base = h.digest()[:self.response_size]
        
        # Adiciona ruído para simular variações físicas
        response_noisy = self._add_noise(response_base)
        
        return PUFResponse(
            response=response_noisy,
            entropy_bits=self.entropy_bits,
            bit_error_rate=self.ber,
            challenge=challenge
        )
    
    def get_entropy(self) -> float:
        """Retorna entropia configurada"""
        return self.entropy_bits
    
    def get_ber(self) -> float:
        """Retorna BER configurada"""
        return self.ber
    
    def get_id(self) -> str:
        """Retorna ID único do PUF"""
        return self.puf_id
    
    def get_stable_response(self, challenge: Optional[bytes] = None) -> bytes:
        """
        Gera resposta estável (sem ruído) para testes
        
        Args:
            challenge: Challenge opcional
        
        Returns:
            Resposta sem ruído
        """
        h = hashlib.sha3_256()
        h.update(self._internal_state)
        
        if challenge is not None:
            h.update(challenge)
        else:
            h.update(b"DEFAULT_CHALLENGE")
        
        return h.digest()[:self.response_size]
    
    def __repr__(self) -> str:
        return (
            f"SimulatedPUF(id={self.puf_id}, "
            f"entropy={self.entropy_bits}bits, "
            f"ber={self.ber:.4f})"
        )
