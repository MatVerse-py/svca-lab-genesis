"""
Ohash - Origin Hash para identidade pública auditável

Cria hash público da identidade física (PUF) que pode ser
registrado em ledger sem revelar a chave privada.
"""

import hashlib
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class OhashRecord:
    """
    Registro de Ohash no ledger
    
    Contém informações públicas sobre a identidade
    sem revelar segredos privados.
    """
    
    ohash: str
    """Hash público da identidade (SHA3-256)"""
    
    timestamp: str
    """Timestamp de criação (ISO 8601)"""
    
    puf_id: str
    """ID público do PUF (não revela chave)"""
    
    entropy_bits: float
    """Entropia declarada em bits"""
    
    algorithm: str = "SHA3-256"
    """Algoritmo de hash usado"""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Metadados adicionais (opcionais)"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "ohash": self.ohash,
            "timestamp": self.timestamp,
            "puf_id": self.puf_id,
            "entropy_bits": self.entropy_bits,
            "algorithm": self.algorithm,
            "metadata": self.metadata
        }
    
    def __repr__(self) -> str:
        return f"OhashRecord(ohash={self.ohash[:16]}..., timestamp={self.timestamp})"


class Ohash:
    """
    Sistema Ohash para identidade pública
    
    Cria hash público de chave privada derivada de PUF.
    Permite verificação de identidade sem revelar segredos.
    
    Propriedades:
    - Unidirecional: Ohash não revela chave privada
    - Único: Cada PUF produz Ohash único
    - Verificável: Qualquer um pode verificar Ohash
    - Imutável: Uma vez registrado, não pode mudar
    """
    
    def __init__(self, algorithm: str = "sha3-256"):
        """
        Inicializa sistema Ohash
        
        Args:
            algorithm: Algoritmo de hash (sha3-256, sha3-512, blake2b)
        """
        self.algorithm = algorithm.lower()
        
        # Mapeia algoritmos para funções
        self.hash_functions = {
            "sha3-256": hashlib.sha3_256,
            "sha3-512": hashlib.sha3_512,
            "blake2b": hashlib.blake2b,
            "sha256": hashlib.sha256,
        }
        
        if self.algorithm not in self.hash_functions:
            raise ValueError(f"Algoritmo não suportado: {algorithm}")
    
    def compute(
        self,
        private_key: bytes,
        salt: Optional[bytes] = None
    ) -> str:
        """
        Computa Ohash de chave privada
        
        Args:
            private_key: Chave privada derivada de PUF
            salt: Salt opcional para fortalecer hash
        
        Returns:
            Ohash em formato hexadecimal
        """
        h = self.hash_functions[self.algorithm]()
        
        # Prefixo de domínio para evitar colisões
        h.update(b"SVCA_OHASH_V1")
        
        # Chave privada
        h.update(private_key)
        
        # Salt opcional
        if salt is not None:
            h.update(salt)
        
        return h.hexdigest()
    
    def create_record(
        self,
        private_key: bytes,
        puf_id: str,
        entropy_bits: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OhashRecord:
        """
        Cria registro completo de Ohash
        
        Args:
            private_key: Chave privada do PUF
            puf_id: ID público do PUF
            entropy_bits: Entropia da chave
            metadata: Metadados adicionais
        
        Returns:
            OhashRecord pronto para registro no ledger
        """
        # Computa Ohash
        ohash = self.compute(private_key)
        
        # Timestamp atual
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Cria registro
        record = OhashRecord(
            ohash=ohash,
            timestamp=timestamp,
            puf_id=puf_id,
            entropy_bits=entropy_bits,
            algorithm=self.algorithm.upper(),
            metadata=metadata or {}
        )
        
        return record
    
    def verify(
        self,
        private_key: bytes,
        claimed_ohash: str,
        salt: Optional[bytes] = None
    ) -> bool:
        """
        Verifica se chave privada corresponde a Ohash
        
        Args:
            private_key: Chave privada a verificar
            claimed_ohash: Ohash alegado
            salt: Salt usado na criação
        
        Returns:
            True se corresponde
        """
        computed_ohash = self.compute(private_key, salt)
        return computed_ohash == claimed_ohash
    
    def compute_commitment(
        self,
        private_key: bytes,
        nonce: bytes
    ) -> str:
        """
        Computa commitment de chave privada com nonce
        
        Usado para provas de conhecimento sem revelar chave.
        
        Args:
            private_key: Chave privada
            nonce: Nonce único
        
        Returns:
            Commitment em hexadecimal
        """
        h = self.hash_functions[self.algorithm]()
        h.update(b"SVCA_COMMITMENT")
        h.update(private_key)
        h.update(nonce)
        return h.hexdigest()
    
    def derive_public_id(self, ohash: str) -> str:
        """
        Deriva ID público curto de Ohash
        
        Args:
            ohash: Ohash completo
        
        Returns:
            ID público curto (primeiros 16 caracteres)
        """
        return ohash[:16]
    
    def __repr__(self) -> str:
        return f"Ohash(algorithm={self.algorithm})"


class OhashLedger:
    """
    Ledger simulado para registros de Ohash
    
    Em produção: integrar com blockchain real (Polygon, Ethereum, etc.)
    """
    
    def __init__(self):
        """Inicializa ledger vazio"""
        self.records: Dict[str, OhashRecord] = {}
        self.creation_time = time.time()
    
    def register(self, record: OhashRecord) -> bool:
        """
        Registra Ohash no ledger
        
        Args:
            record: Registro a adicionar
        
        Returns:
            True se registrado com sucesso
        """
        if record.ohash in self.records:
            # Ohash já existe (colisão ou re-registro)
            return False
        
        self.records[record.ohash] = record
        return True
    
    def lookup(self, ohash: str) -> Optional[OhashRecord]:
        """
        Busca registro por Ohash
        
        Args:
            ohash: Ohash a buscar
        
        Returns:
            Registro se encontrado, None caso contrário
        """
        return self.records.get(ohash)
    
    def exists(self, ohash: str) -> bool:
        """
        Verifica se Ohash existe no ledger
        
        Args:
            ohash: Ohash a verificar
        
        Returns:
            True se existe
        """
        return ohash in self.records
    
    def get_all_records(self) -> list[OhashRecord]:
        """
        Retorna todos os registros
        
        Returns:
            Lista de registros
        """
        return list(self.records.values())
    
    def count(self) -> int:
        """
        Conta registros no ledger
        
        Returns:
            Número de registros
        """
        return len(self.records)
    
    def __repr__(self) -> str:
        return f"OhashLedger(records={len(self.records)})"
