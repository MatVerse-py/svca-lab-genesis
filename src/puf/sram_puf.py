"""
SRAM PUF - Simulação de PUF baseado em SRAM

Simula PUF que usa estado de inicialização aleatório de células SRAM
causado por variações de fabricação em nível nanométrico.

Aplicação: Chips NFC, microcontroladores, hardware embarcado
"""

import hashlib
import secrets
import numpy as np
from typing import Optional
from .puf_base import PUFResponse


class SRAMPUF:
    """
    SRAM PUF simulado
    
    Simula comportamento de células SRAM ao ligar (power-up):
    - Cada célula tende a inicializar em 0 ou 1 (viés de fabricação)
    - Ruído térmico causa variações (~1-5% das células)
    - Padrão único por chip
    
    Propriedades:
    - Entropia moderada (limitada por tamanho da SRAM)
    - BER baixo (células estáveis)
    - Fácil integração em hardware existente
    """
    
    def __init__(
        self,
        chip_seed: Optional[int] = None,
        sram_size: int = 1024,  # bytes
        entropy_bits: float = 256.0,
        ber: float = 0.02
    ):
        """
        Inicializa SRAM PUF
        
        Args:
            chip_seed: Seed representando variações de fabricação
            sram_size: Tamanho da SRAM em bytes
            entropy_bits: Entropia das células instáveis
            ber: Taxa de erro (células que mudam entre power-ups)
        """
        if chip_seed is None:
            chip_seed = secrets.randbits(256)
        
        self.chip_seed = chip_seed
        self.sram_size = sram_size
        self.entropy_bits = entropy_bits
        self.ber = max(0.0, min(0.5, ber))
        
        # Gera ID do chip
        self.puf_id = hashlib.sha3_256(
            chip_seed.to_bytes(32, 'big')
        ).hexdigest()[:16]
        
        # Gera viés de cada célula (variações de fabricação)
        np.random.seed(chip_seed % (2**32))
        self.cell_bias = self._generate_cell_bias()
    
    def _generate_cell_bias(self) -> np.ndarray:
        """
        Gera viés de inicialização de cada célula SRAM
        
        Cada célula tem probabilidade p de inicializar em 1:
        - p ≈ 0.0: célula sempre inicia em 0
        - p ≈ 0.5: célula instável (alta entropia)
        - p ≈ 1.0: célula sempre inicia em 1
        
        Returns:
            Array com probabilidades [0.0, 1.0] para cada bit
        """
        total_bits = self.sram_size * 8
        
        # Distribuição beta para simular variações de fabricação
        # Maioria das células é estável (próximo de 0 ou 1)
        # Algumas células são instáveis (próximo de 0.5)
        alpha = 0.5  # Parâmetros para distribuição bimodal
        beta = 0.5
        bias = np.random.beta(alpha, beta, total_bits)
        
        return bias
    
    def _power_up_state(self) -> bytes:
        """
        Simula estado de power-up da SRAM
        
        Cada célula inicializa baseado em seu viés + ruído térmico
        
        Returns:
            Estado inicial da SRAM em bytes
        """
        total_bits = self.sram_size * 8
        
        # Gera estado baseado em viés + ruído
        random_values = np.random.random(total_bits)
        state_bits = (random_values < self.cell_bias).astype(np.uint8)
        
        # Converte array de bits para bytes
        state_int = int(''.join(state_bits.astype(str)), 2)
        state_bytes = state_int.to_bytes(self.sram_size, 'big')
        
        return state_bytes
    
    def _add_thermal_noise(self, state: bytes) -> bytes:
        """
        Adiciona ruído térmico (células que mudam entre power-ups)
        
        Args:
            state: Estado base
        
        Returns:
            Estado com ruído térmico
        """
        if self.ber == 0.0:
            return state
        
        # Converte para bits
        bits = int.from_bytes(state, 'big')
        total_bits = len(state) * 8
        
        # Flipa bits aleatórios (ruído térmico)
        num_flips = int(total_bits * self.ber)
        for _ in range(num_flips):
            bit_pos = secrets.randbelow(total_bits)
            bits ^= (1 << bit_pos)
        
        return bits.to_bytes(len(state), 'big')
    
    def generate(self, challenge: Optional[bytes] = None) -> PUFResponse:
        """
        Gera resposta do SRAM PUF (simula power-up)
        
        Args:
            challenge: Endereço de memória ou região a ler
        
        Returns:
            PUFResponse com estado de power-up
        """
        # Simula power-up
        state = self._power_up_state()
        
        # Se houver challenge, seleciona região específica
        if challenge is not None:
            # Usa challenge como offset
            offset = int.from_bytes(challenge[:2], 'big') if len(challenge) >= 2 else 0
            offset = offset % self.sram_size
            
            # Lê 32 bytes a partir do offset (circular)
            region = bytearray()
            for i in range(32):
                region.append(state[(offset + i) % self.sram_size])
            state = bytes(region)
        
        # Adiciona ruído térmico
        noisy_state = self._add_thermal_noise(state)
        
        # Hash para comprimir mantendo entropia
        h = hashlib.sha3_256()
        h.update(noisy_state)
        response = h.digest()
        
        return PUFResponse(
            response=response,
            entropy_bits=self.entropy_bits,
            bit_error_rate=self.ber,
            challenge=challenge
        )
    
    def get_entropy(self) -> float:
        """Retorna entropia das células instáveis"""
        return self.entropy_bits
    
    def get_ber(self) -> float:
        """Retorna taxa de erro térmico"""
        return self.ber
    
    def get_id(self) -> str:
        """Retorna ID do chip"""
        return self.puf_id
    
    def get_cell_stability(self) -> np.ndarray:
        """
        Retorna estabilidade de cada célula
        
        Estabilidade = distância de 0.5 (células próximas de 0.5 são instáveis)
        
        Returns:
            Array com estabilidade [0.0, 0.5] para cada bit
        """
        return np.abs(self.cell_bias - 0.5)
    
    def get_unstable_cells(self, threshold: float = 0.1) -> int:
        """
        Conta células instáveis (alta entropia)
        
        Args:
            threshold: Distância de 0.5 para considerar instável
        
        Returns:
            Número de células instáveis
        """
        stability = self.get_cell_stability()
        return np.sum(stability < threshold)
    
    def __repr__(self) -> str:
        return (
            f"SRAMPUF(id={self.puf_id}, "
            f"size={self.sram_size}B, "
            f"entropy={self.entropy_bits}bits, "
            f"ber={self.ber:.4f})"
        )
