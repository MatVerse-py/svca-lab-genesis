"""
Optical PUF - Simulação de PUF óptico

Simula PUF baseado em padrões de speckle óptico causados por
micro-rachaduras e variações em materiais transparentes.

Aplicações CORE B DAY:
- Fibra de seringueira (Acre)
- PET solarizado (Alagoas)
- Casca de árvore (Amazonas)
"""

import hashlib
import secrets
import numpy as np
from typing import Optional
from .puf_base import PUFResponse


class OpticalPUF:
    """
    PUF Óptico simulado
    
    Simula padrões de speckle gerados por laser atravessando
    material com micro-estruturas aleatórias.
    
    Propriedades:
    - Alta entropia (padrões de interferência complexos)
    - BER moderado (variações de iluminação/posicionamento)
    - Resposta visual única
    """
    
    def __init__(
        self,
        material_seed: Optional[int] = None,
        speckle_size: int = 64,
        entropy_bits: float = 512.0,
        ber: float = 0.05
    ):
        """
        Inicializa PUF óptico
        
        Args:
            material_seed: Seed representando estrutura física do material
            speckle_size: Tamanho do padrão de speckle (pixels)
            entropy_bits: Entropia do padrão óptico
            ber: Taxa de erro devido a variações de medição
        """
        if material_seed is None:
            material_seed = secrets.randbits(512)
        
        self.material_seed = material_seed
        self.speckle_size = speckle_size
        self.entropy_bits = entropy_bits
        self.ber = max(0.0, min(0.5, ber))
        
        # Gera ID baseado na estrutura do material
        self.puf_id = hashlib.sha3_256(
            material_seed.to_bytes(64, 'big')
        ).hexdigest()[:16]
        
        # Gera padrão de speckle base (estrutura física)
        np.random.seed(material_seed % (2**32))
        self.speckle_pattern = self._generate_speckle_pattern()
    
    def _generate_speckle_pattern(self) -> np.ndarray:
        """
        Gera padrão de speckle simulado
        
        Simula interferência de laser através de meio com
        micro-estruturas aleatórias.
        
        Returns:
            Array 2D com padrão de intensidade
        """
        # Fase aleatória (micro-estruturas)
        phase = np.random.uniform(0, 2*np.pi, (self.speckle_size, self.speckle_size))
        
        # Amplitude (variações de densidade)
        amplitude = np.random.rayleigh(1.0, (self.speckle_size, self.speckle_size))
        
        # Padrão de interferência (simplificado)
        # Em PUF real: transformada de Fourier de campo complexo
        pattern = amplitude * np.cos(phase)
        
        # Normaliza para [0, 255]
        pattern = ((pattern - pattern.min()) / (pattern.max() - pattern.min()) * 255)
        
        return pattern.astype(np.uint8)
    
    def _add_measurement_noise(self, pattern: np.ndarray) -> np.ndarray:
        """
        Adiciona ruído de medição (iluminação, posicionamento, sensor)
        
        Args:
            pattern: Padrão original
        
        Returns:
            Padrão com ruído de medição
        """
        if self.ber == 0.0:
            return pattern
        
        # Ruído gaussiano (variações de iluminação)
        noise_std = self.ber * 255
        noise = np.random.normal(0, noise_std, pattern.shape)
        
        # Aplica ruído e limita a [0, 255]
        noisy = pattern + noise
        noisy = np.clip(noisy, 0, 255)
        
        return noisy.astype(np.uint8)
    
    def _pattern_to_bytes(self, pattern: np.ndarray) -> bytes:
        """Converte padrão 2D em bytes"""
        # Usa hash para comprimir padrão mantendo entropia
        h = hashlib.sha3_512()
        h.update(pattern.tobytes())
        return h.digest()
    
    def generate(self, challenge: Optional[bytes] = None) -> PUFResponse:
        """
        Gera resposta do PUF óptico
        
        Args:
            challenge: Posição de leitura ou parâmetros de laser
        
        Returns:
            PUFResponse com hash do padrão de speckle
        """
        # Padrão base (estrutura física)
        pattern = self.speckle_pattern.copy()
        
        # Se houver challenge, modifica região de leitura
        if challenge is not None:
            # Usa challenge para selecionar região
            region_seed = int.from_bytes(challenge[:4], 'big') if len(challenge) >= 4 else 0
            np.random.seed(region_seed)
            
            # Seleciona sub-região aleatória
            size = self.speckle_size // 2
            x = np.random.randint(0, self.speckle_size - size)
            y = np.random.randint(0, self.speckle_size - size)
            pattern = pattern[y:y+size, x:x+size]
        
        # Adiciona ruído de medição
        noisy_pattern = self._add_measurement_noise(pattern)
        
        # Converte para bytes
        response = self._pattern_to_bytes(noisy_pattern)
        
        return PUFResponse(
            response=response,
            entropy_bits=self.entropy_bits,
            bit_error_rate=self.ber,
            challenge=challenge
        )
    
    def get_entropy(self) -> float:
        """Retorna entropia do padrão óptico"""
        return self.entropy_bits
    
    def get_ber(self) -> float:
        """Retorna BER de medição"""
        return self.ber
    
    def get_id(self) -> str:
        """Retorna ID do material"""
        return self.puf_id
    
    def get_speckle_pattern(self) -> np.ndarray:
        """
        Retorna padrão de speckle base (para visualização)
        
        Returns:
            Array 2D com padrão de intensidade
        """
        return self.speckle_pattern.copy()
    
    def __repr__(self) -> str:
        return (
            f"OpticalPUF(id={self.puf_id}, "
            f"size={self.speckle_size}x{self.speckle_size}, "
            f"entropy={self.entropy_bits}bits, "
            f"ber={self.ber:.4f})"
        )
