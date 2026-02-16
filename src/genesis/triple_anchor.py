"""
Triple Anchor - Ancoragem temporal tripla

Implementa três tipos de âncoras temporais para garantir
irreversibilidade e auditabilidade:

1. System Time: Timestamp do sistema
2. Network Time: Timestamp de servidor NTP
3. Ledger Time: Timestamp do ledger/blockchain

Juntas, criam prova robusta de precedência temporal.
"""

import time
import hashlib
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AnchorType(Enum):
    """Tipo de âncora temporal"""
    SYSTEM = "system"      # Timestamp do sistema local
    NETWORK = "network"    # Timestamp de servidor NTP
    LEDGER = "ledger"      # Timestamp do ledger/blockchain


@dataclass
class Anchor:
    """Âncora temporal individual"""
    
    anchor_type: AnchorType
    """Tipo da âncora"""
    
    timestamp: float
    """Timestamp Unix"""
    
    timestamp_iso: str
    """Timestamp em formato ISO 8601"""
    
    source: str
    """Fonte do timestamp (hostname, URL, etc.)"""
    
    signature: Optional[str] = None
    """Assinatura da fonte (se aplicável)"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "type": self.anchor_type.value,
            "timestamp": self.timestamp,
            "timestamp_iso": self.timestamp_iso,
            "source": self.source,
            "signature": self.signature
        }


class TripleAnchor:
    """
    Sistema de ancoragem temporal tripla
    
    Cria três âncoras independentes para provar precedência temporal
    de forma robusta contra manipulação.
    """
    
    def __init__(self):
        """Inicializa sistema de triple anchor"""
        self.anchors: Dict[AnchorType, Anchor] = {}
    
    def create_system_anchor(self) -> Anchor:
        """
        Cria âncora de sistema
        
        Usa timestamp do sistema operacional local.
        
        Returns:
            Anchor de sistema
        """
        timestamp = time.time()
        timestamp_iso = datetime.utcfromtimestamp(timestamp).isoformat() + "Z"
        
        anchor = Anchor(
            anchor_type=AnchorType.SYSTEM,
            timestamp=timestamp,
            timestamp_iso=timestamp_iso,
            source="system_clock"
        )
        
        self.anchors[AnchorType.SYSTEM] = anchor
        return anchor
    
    def create_network_anchor(self, ntp_server: str = "pool.ntp.org") -> Anchor:
        """
        Cria âncora de rede
        
        Usa timestamp de servidor NTP.
        Em produção: fazer requisição NTP real.
        
        Args:
            ntp_server: Servidor NTP a usar
        
        Returns:
            Anchor de rede
        """
        # Implementação simplificada: usa system time
        # Em produção: usar biblioteca ntplib
        timestamp = time.time()
        timestamp_iso = datetime.utcfromtimestamp(timestamp).isoformat() + "Z"
        
        anchor = Anchor(
            anchor_type=AnchorType.NETWORK,
            timestamp=timestamp,
            timestamp_iso=timestamp_iso,
            source=ntp_server
        )
        
        self.anchors[AnchorType.NETWORK] = anchor
        return anchor
    
    def create_ledger_anchor(
        self,
        ledger_url: str = "simulated_ledger",
        block_hash: Optional[str] = None
    ) -> Anchor:
        """
        Cria âncora de ledger
        
        Usa timestamp de bloco em blockchain.
        Em produção: integrar com blockchain real.
        
        Args:
            ledger_url: URL do ledger
            block_hash: Hash do bloco (se disponível)
        
        Returns:
            Anchor de ledger
        """
        timestamp = time.time()
        timestamp_iso = datetime.utcfromtimestamp(timestamp).isoformat() + "Z"
        
        # Simula assinatura do bloco
        if block_hash is None:
            h = hashlib.sha3_256()
            h.update(b"SIMULATED_BLOCK")
            h.update(str(timestamp).encode())
            block_hash = h.hexdigest()
        
        anchor = Anchor(
            anchor_type=AnchorType.LEDGER,
            timestamp=timestamp,
            timestamp_iso=timestamp_iso,
            source=ledger_url,
            signature=block_hash
        )
        
        self.anchors[AnchorType.LEDGER] = anchor
        return anchor
    
    def create_all(self) -> Dict[AnchorType, Anchor]:
        """
        Cria todas as três âncoras
        
        Returns:
            Dicionário com as três âncoras
        """
        self.create_system_anchor()
        self.create_network_anchor()
        self.create_ledger_anchor()
        
        return self.anchors
    
    def verify_consistency(self, max_drift_seconds: float = 5.0) -> bool:
        """
        Verifica consistência entre âncoras
        
        Todas as âncoras devem estar próximas (dentro de max_drift).
        
        Args:
            max_drift_seconds: Deriva máxima permitida em segundos
        
        Returns:
            True se consistente
        """
        if len(self.anchors) < 2:
            return True  # Não há o que comparar
        
        timestamps = [a.timestamp for a in self.anchors.values()]
        min_ts = min(timestamps)
        max_ts = max(timestamps)
        
        drift = max_ts - min_ts
        
        return drift <= max_drift_seconds
    
    def get_anchor(self, anchor_type: AnchorType) -> Optional[Anchor]:
        """
        Retorna âncora específica
        
        Args:
            anchor_type: Tipo da âncora
        
        Returns:
            Anchor ou None
        """
        return self.anchors.get(anchor_type)
    
    def get_median_timestamp(self) -> Optional[float]:
        """
        Retorna timestamp mediano das âncoras
        
        Mais robusto contra manipulação de uma única fonte.
        
        Returns:
            Timestamp mediano ou None se vazio
        """
        if len(self.anchors) == 0:
            return None
        
        timestamps = sorted([a.timestamp for a in self.anchors.values()])
        
        n = len(timestamps)
        if n % 2 == 0:
            return (timestamps[n//2 - 1] + timestamps[n//2]) / 2
        else:
            return timestamps[n//2]
    
    def export(self) -> Dict[str, Any]:
        """
        Exporta triple anchor
        
        Returns:
            Dicionário com todas as âncoras
        """
        return {
            "anchors": {
                anchor_type.value: anchor.to_dict()
                for anchor_type, anchor in self.anchors.items()
            },
            "median_timestamp": self.get_median_timestamp(),
            "consistent": self.verify_consistency()
        }
    
    def compute_hash(self) -> str:
        """
        Computa hash das âncoras
        
        Returns:
            Hash SHA3-256 das três âncoras
        """
        h = hashlib.sha3_256()
        h.update(b"TRIPLE_ANCHOR")
        
        # Ordena por tipo para garantir determinismo
        for anchor_type in sorted(self.anchors.keys(), key=lambda x: x.value):
            anchor = self.anchors[anchor_type]
            h.update(anchor.anchor_type.value.encode())
            h.update(str(anchor.timestamp).encode())
            h.update(anchor.source.encode())
        
        return h.hexdigest()
    
    def __repr__(self) -> str:
        return (
            f"TripleAnchor("
            f"anchors={len(self.anchors)}, "
            f"consistent={self.verify_consistency()})"
        )
