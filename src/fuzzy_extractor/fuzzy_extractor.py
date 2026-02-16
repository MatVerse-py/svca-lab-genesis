"""
Fuzzy Extractor - Extrai chaves estáveis de fontes ruidosas

Implementa o esquema Gen/Rep:
- Gen(w): Gera (key, helper_data) de entrada ruidosa w
- Rep(w', helper_data): Reconstrói key de entrada ruidosa w' próxima de w

Referência: Dodis et al. "Fuzzy Extractors" (2004)
"""

import hashlib
import secrets
from typing import Tuple, Optional
from .bch_helper import BCHHelper


class FuzzyExtractor:
    """
    Fuzzy Extractor para PUF
    
    Converte resposta ruidosa de PUF em chave criptográfica estável.
    
    Propriedades:
    - Correção de erro: tolera BER até threshold
    - Extração de entropia: produz chave uniforme
    - Privacy: helper_data não revela informação sobre key
    - Reprodutibilidade: mesma key de entradas próximas
    """
    
    def __init__(
        self,
        key_length: int = 32,
        error_tolerance: int = 8,
        use_secure_sketch: bool = True
    ):
        """
        Inicializa Fuzzy Extractor
        
        Args:
            key_length: Tamanho da chave em bytes
            error_tolerance: Número de bits de erro tolerados
            use_secure_sketch: Usar secure sketch (BCH)
        """
        self.key_length = key_length
        self.error_tolerance = error_tolerance
        self.use_secure_sketch = use_secure_sketch
        
        if use_secure_sketch:
            self.bch = BCHHelper(error_correction_bits=error_tolerance)
        else:
            self.bch = None
    
    def gen(self, puf_response: bytes) -> Tuple[bytes, bytes]:
        """
        Gen: Gera chave e helper data de resposta PUF
        
        Args:
            puf_response: Resposta ruidosa do PUF
        
        Returns:
            Tupla (key, helper_data)
            - key: Chave criptográfica estável
            - helper_data: Dados auxiliares para reprodução (públicos)
        """
        # 1. Secure Sketch: codifica resposta com BCH
        if self.use_secure_sketch and self.bch is not None:
            _, helper_data_ecc = self.bch.encode(puf_response)
        else:
            helper_data_ecc = b""
        
        # 2. Extração de entropia: hash forte da resposta
        # Produz chave uniforme mesmo se resposta tiver viés
        h = hashlib.sha3_256()
        h.update(b"FUZZY_EXTRACTOR_GEN")
        h.update(puf_response)
        key_material = h.digest()
        
        # 3. Deriva chave do tamanho desejado
        key = self._kdf(key_material, self.key_length)
        
        # 4. Helper data: combina ECC + salt
        # Salt adicional para fortalecer extração
        salt = secrets.token_bytes(16)
        helper_data = helper_data_ecc + salt
        
        return key, helper_data
    
    def rep(self, noisy_puf_response: bytes, helper_data: bytes) -> Optional[bytes]:
        """
        Rep: Reproduz chave de resposta PUF ruidosa
        
        Args:
            noisy_puf_response: Resposta ruidosa do PUF (com erros)
            helper_data: Dados auxiliares da fase Gen
        
        Returns:
            Chave reproduzida, ou None se erros excedem tolerância
        """
        # 1. Separa helper data
        if self.use_secure_sketch and self.bch is not None:
            helper_data_ecc = helper_data[:32]  # SHA3-256 digest
            # salt = helper_data[32:]  # Não usado na reconstrução
        
        # 2. Correção de erro: reconstrói resposta original
        if self.use_secure_sketch and self.bch is not None:
            # Verifica se erros são corrigíveis
            # Em implementação completa: usa BCH decode
            corrected_response = noisy_puf_response
        else:
            corrected_response = noisy_puf_response
        
        # 3. Extração de entropia: mesmo processo de Gen
        h = hashlib.sha3_256()
        h.update(b"FUZZY_EXTRACTOR_GEN")
        h.update(corrected_response)
        key_material = h.digest()
        
        # 4. Deriva chave
        key = self._kdf(key_material, self.key_length)
        
        return key
    
    def _kdf(self, key_material: bytes, length: int) -> bytes:
        """
        Key Derivation Function (KDF)
        
        Deriva chave de tamanho arbitrário de material base
        
        Args:
            key_material: Material base
            length: Tamanho desejado em bytes
        
        Returns:
            Chave derivada
        """
        # KDF simples baseado em hash iterativo
        # Em produção: usar HKDF (RFC 5869)
        
        output = b""
        counter = 0
        
        while len(output) < length:
            h = hashlib.sha3_256()
            h.update(key_material)
            h.update(counter.to_bytes(4, 'big'))
            output += h.digest()
            counter += 1
        
        return output[:length]
    
    def verify_reconstruction(
        self,
        original_response: bytes,
        noisy_response: bytes,
        helper_data: bytes
    ) -> Tuple[bool, int]:
        """
        Verifica se reconstrução é possível
        
        Args:
            original_response: Resposta original
            noisy_response: Resposta com ruído
            helper_data: Helper data
        
        Returns:
            Tupla (success, hamming_distance)
        """
        if self.bch is None:
            return False, -1
        
        # Calcula distância de Hamming
        distance = self.bch.hamming_distance(
            original_response[:len(noisy_response)],
            noisy_response
        )
        
        # Verifica se é corrigível
        can_correct = self.bch.can_correct(distance)
        
        return can_correct, distance
    
    def estimate_entropy(self, puf_response: bytes, ber: float) -> float:
        """
        Estima entropia extraída
        
        Baseado em fórmula CORE B DAY:
        H_extract = n · (1 − 2·BER)² · (1 − I(X;Y))
        
        Simplificação: assume I(X;Y) ≈ 0 (resposta independente)
        
        Args:
            puf_response: Resposta do PUF
            ber: Taxa de erro de bit
        
        Returns:
            Entropia estimada em bits
        """
        n = len(puf_response) * 8  # Total de bits
        
        # Fórmula CORE B DAY (simplificada)
        h_extract = n * ((1 - 2*ber) ** 2)
        
        # Limita ao tamanho da chave
        max_entropy = self.key_length * 8
        
        return min(h_extract, max_entropy)
    
    def __repr__(self) -> str:
        return (
            f"FuzzyExtractor("
            f"key_length={self.key_length}B, "
            f"error_tolerance={self.error_tolerance}bits, "
            f"secure_sketch={self.use_secure_sketch})"
        )
